
from backend.retriever import (
    bm25_search,
    hybrid_search,
    rerank_results,
    retrieve_relevant_documents
)

from backend.retriever import load_chunks


# ==========================================
# PASUMAI AI BOT - RETRIEVER TEST
# ==========================================

question = (
    "What financial assistance is available "
    "for farmers under PM-KISAN?"
)


# STEP 1: LOAD DOCUMENTS

print("\nSTEP 1: Loading documents...")

chunks = load_chunks()

print("Total chunks:", len(chunks))


# STEP 2: TEST BM25

print("\nSTEP 2: Testing BM25...")

bm25_results = bm25_search(
    question,
    chunks,
    top_k=5
)

print("BM25 results:", len(bm25_results))


# STEP 3: TEST HYBRID SEARCH

print("\nSTEP 3: Testing hybrid search...")

hybrid_results = hybrid_search(question)

print("Hybrid results:", len(hybrid_results))


# STEP 4: TEST CROSSENCODER

print("\nSTEP 4: Testing reranking...")

reranked_results = rerank_results(
    question,
    hybrid_results,
    top_k=5
)

print("Reranked results:", len(reranked_results))


# STEP 5: COMPLETE PIPELINE

print("\nSTEP 5: Complete retrieval pipeline...")

final_results = retrieve_relevant_documents(
    question,
    top_k=5
)


# DISPLAY RESULTS

print("\nFINAL SEARCH RESULTS")

for i, result in enumerate(
    final_results,
    start=1
):

    print("\n-----------------------------")

    print("Result:", i)

    print("Source:", result["source"])

    print("Page:", result["page"])

    print(
        "Rerank score:",
        round(result["rerank_score"], 4)
    )

    print("Text:", result["text"][:400])


print("\nHYBRID RETRIEVAL TEST COMPLETED!")
