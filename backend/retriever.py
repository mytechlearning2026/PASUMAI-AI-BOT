
import re

from rank_bm25 import BM25Okapi

from sentence_transformers import CrossEncoder

from backend.vector_store import semantic_search


# ==========================================
# PASUMAI AI BOT - HYBRID RETRIEVER
# ==========================================

BM25_TOP_K = 5

FAISS_TOP_K = 5

FINAL_TOP_K = 5

RERANKER_MODEL = (
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# ==========================================
# 1. TOKENIZE TEXT FOR BM25
# ==========================================

def tokenize(text):

    return re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower()
    )


# ==========================================
# 2. LOAD CROSSENCODER MODEL
# ==========================================

_reranker = None


def get_reranker():

    global _reranker

    if _reranker is None:

        print("Loading CrossEncoder model...")

        _reranker = CrossEncoder(
            RERANKER_MODEL
        )

        print("CrossEncoder loaded successfully!")

    return _reranker


# ==========================================
# 3. LOAD CHUNKS FROM FAISS METADATA
# ==========================================

def load_chunks():

    from backend.vector_store import load_vector_store

    index, chunks = load_vector_store()

    return chunks


# ==========================================
# 4. BM25 KEYWORD RETRIEVAL
# ==========================================

def bm25_search(query, chunks, top_k=BM25_TOP_K):

    if not chunks:
        return []

    tokenized_corpus = [

        tokenize(chunk["text"])

        for chunk in chunks

    ]

    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = tokenize(query)

    if not tokenized_query:
        return []

    scores = bm25.get_scores(tokenized_query)

    ranked_indices = sorted(

        range(len(scores)),

        key=lambda i: scores[i],

        reverse=True

    )[:top_k]

    results = []

    for idx in ranked_indices:

        if scores[idx] <= 0:
            continue

        result = chunks[idx].copy()

        result["bm25_score"] = float(scores[idx])

        results.append(result)

    return results


# ==========================================
# 5. HYBRID RETRIEVAL
# ==========================================

def hybrid_search(query):

    print("\nStarting hybrid retrieval...")

    chunks = load_chunks()

    if not chunks:
        return []

    # BM25 keyword search

    print("Running BM25 search...")

    bm25_results = bm25_search(
        query,
        chunks,
        BM25_TOP_K
    )

    # FAISS semantic search

    print("Running FAISS semantic search...")

    faiss_results = semantic_search(
        query,
        top_k=FAISS_TOP_K
    )

    # Combine both result sets

    combined = {}

    for result in bm25_results + faiss_results:

        key = result["id"]

        if key not in combined:

            combined[key] = result.copy()

        else:

            combined[key].update(result)

    results = list(combined.values())

    print("BM25 results:", len(bm25_results))

    print("FAISS results:", len(faiss_results))

    print("Combined results:", len(results))

    return results


# ==========================================
# 6. CROSSENCODER RERANKING
# ==========================================

def rerank_results(query, results, top_k=FINAL_TOP_K):

    if not results:
        return []

    print("\nStarting CrossEncoder reranking...")

    model = get_reranker()

    pairs = [

        [query, result["text"]]

        for result in results

    ]

    scores = model.predict(pairs)

    reranked = []

    for result, score in zip(results, scores):

        updated = result.copy()

        updated["rerank_score"] = float(score)

        reranked.append(updated)

    reranked.sort(

        key=lambda x: x["rerank_score"],

        reverse=True

    )

    print("Reranking completed!")

    return reranked[:top_k]


# ==========================================
# 7. COMPLETE RETRIEVAL PIPELINE
# ==========================================

def retrieve_relevant_documents(query, top_k=FINAL_TOP_K):

    # Hybrid search

    results = hybrid_search(query)

    # CrossEncoder reranking

    final_results = rerank_results(
        query,
        results,
        top_k
    )

    return final_results
