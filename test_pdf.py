
from backend.document_processor import process_pdf


# Original government schemes PDF
PDF_PATH = "data/schemes/all_30_schemes.pdf"


print("\nPASUMAI AI BOT")
print("PDF DOCUMENT PROCESSING TEST")


# Process PDF
chunks = process_pdf(PDF_PATH)


# Display results
print("\nFIRST 3 CHUNKS")

for chunk in chunks[:3]:

    print("\n---------------------------")

    print("Chunk ID:", chunk["id"])

    print("Source:", chunk["source"])

    print("Page:", chunk["page"])

    print("Text:", chunk["text"][:300])


print("\n---------------------------")

print("SUCCESS!")

print("Total chunks:", len(chunks))

print("PDF PROCESSING TEST COMPLETED!")
