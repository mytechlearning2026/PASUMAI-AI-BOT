
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# ==========================================
# PASUMAI AI BOT - FAISS VECTOR STORE
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

FAISS_DIR = BASE_DIR / "data" / "faiss_index"

INDEX_PATH = FAISS_DIR / "index.faiss"

METADATA_PATH = FAISS_DIR / "chunks.json"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

EMBEDDING_DIMENSION = 384

TOP_K = 5


# ==========================================
# 1. LOAD SENTENCE TRANSFORMER MODEL
# ==========================================

_model = None


def get_embedding_model():

    global _model

    if _model is None:

        print("Loading embedding model...")

        _model = SentenceTransformer(MODEL_NAME)

        print("Embedding model loaded successfully!")

    return _model


# ==========================================
# 2. GENERATE EMBEDDINGS
# ==========================================

def generate_embeddings(texts):

    if not texts:
        raise ValueError("No text provided for embeddings.")

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return np.asarray(embeddings, dtype="float32")


# ==========================================
# 3. BUILD FAISS DATABASE
# ==========================================

def build_vector_store(chunks):

    if not chunks:

        raise ValueError("No chunks available.")

    FAISS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    texts = [
        chunk["text"] for chunk in chunks
    ]

    print("\nGenerating embeddings...")

    embeddings = generate_embeddings(texts)

    # Inner product on normalized vectors
    # gives cosine similarity

    index = faiss.IndexFlatIP(
        EMBEDDING_DIMENSION
    )

    index.add(embeddings)

    # Save FAISS index

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )

    # Save chunk metadata

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\nFAISS database created!")

    print("Total vectors:", index.ntotal)

    print("Index saved:", INDEX_PATH)

    return index


# ==========================================
# 4. LOAD EXISTING FAISS DATABASE
# ==========================================

def load_vector_store():

    if not INDEX_PATH.exists():

        raise FileNotFoundError(
            "FAISS index not found. Build it first."
        )

    if not METADATA_PATH.exists():

        raise FileNotFoundError(
            "Chunk metadata not found."
        )

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    if index.ntotal != len(chunks):

        raise ValueError(
            "FAISS index and metadata count mismatch."
        )

    return index, chunks


# ==========================================
# 5. SEMANTIC SEARCH
# ==========================================

def semantic_search(query, top_k=TOP_K):

    index, chunks = load_vector_store()

    if index.ntotal == 0:
        return []

    query_embedding = generate_embeddings(
        [query]
    )

    scores, indices = index.search(
        query_embedding,
        min(top_k, index.ntotal)
    )

    results = []

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx == -1:
            continue

        result = chunks[int(idx)].copy()

        result["similarity_score"] = float(score)

        results.append(result)

    return results


# ==========================================
# 6. DATABASE STATUS
# ==========================================

def get_vector_store_status():

    if not INDEX_PATH.exists():

        return {
            "status": "Not created",
            "total_vectors": 0
        }

    index, chunks = load_vector_store()

    return {

        "status": "Ready",

        "total_vectors": index.ntotal,

        "total_chunks": len(chunks),

        "embedding_model": MODEL_NAME,

        "embedding_dimension": EMBEDDING_DIMENSION

    }
