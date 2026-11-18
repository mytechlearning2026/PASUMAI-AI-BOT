
from backend.document_processor import process_pdf

from backend.vector_store import (
    build_vector_store,
    get_vector_store_status,
    semantic_search
)


# ==========================================
# PASUMAI AI BOT - FAISS TEST
# ==========================================

PDF_PATH = "data/schemes/all_30_schemes.pdf"


# STEP 1: PROCESS PDF

print("\nSTEP 1: Processing PDF...")

chunks = process_pdf(PDF_PATH)


# STEP 2: BUILD VECTOR DATABASE

print("\nSTEP 2: Building FAISS database...")

build_vector_store(chunks)


# STEP 3: CHECK DATABASE

print("\nSTEP 3: Checking FAISS status...")

status = get_vector_store_status()

print(status)


# STEP 4: TEST SEMANTIC SEARCH

print("\nSTEP 4: Testing semantic search...")

question = "What is PM-KISAN and who is eligible?"

results = semantic_search(
    question,
    top_k=5
)


# STEP 5: DISPLAY RESULTS

print("\nSEARCH RESULTS")

for i, result in enumerate(
    results, start=1
):

    print("\nResult:", i)

    print("Source:", result["source"])

    print("Page:", result["page"])

    print(
        "Similarity:",
        round(result["similarity_score"], 4)
    )

    print("Text:", result["text"][:400])


print("\nFAISS TEST COMPLETED SUCCESSFULLY!")
