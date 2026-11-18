
import re
from pathlib import Path
from io import BytesIO
from pypdf import PdfReader


# ==========================================
# PASUMAI AI BOT - DOCUMENT PROCESSOR
# ==========================================

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


# ==========================================
# 1. CLEAN TEXT
# ==========================================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================
# 2. EXTRACT PDF FROM FILE PATH
# ==========================================

def extract_pdf(pdf_path):

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    reader = PdfReader(str(pdf_path))

    documents = []

    total_pages = len(reader.pages)

    for page_number, page in enumerate(
        reader.pages, start=1
    ):

        text = page.extract_text() or ""

        text = clean_text(text)

        if text:

            documents.append({

                "text": text,

                "source": pdf_path.name,

                "page": page_number

            })

    if not documents:

        raise ValueError(
            "No readable text found in PDF. "
            "The PDF may contain scanned images."
        )

    print("\nPDF PROCESSING COMPLETED")

    print("File:", pdf_path.name)

    print("Total PDF Pages:", total_pages)

    print("Pages With Text:", len(documents))

    return documents


# ==========================================
# 3. EXTRACT PDF FROM UPLOADED FILE BYTES
# ==========================================

def extract_pdf_bytes(pdf_bytes, filename):

    reader = PdfReader(BytesIO(pdf_bytes))

    documents = []

    for page_number, page in enumerate(
        reader.pages, start=1
    ):

        text = page.extract_text() or ""

        text = clean_text(text)

        if text:

            documents.append({

                "text": text,

                "source": filename,

                "page": page_number

            })

    if not documents:

        raise ValueError(
            "No readable text found in uploaded PDF."
        )

    print(
        f"Uploaded PDF processed: {filename}"
    )

    return documents


# ==========================================
# 4. SPLIT TEXT INTO CHUNKS
# ==========================================

def split_into_chunks(documents):

    all_chunks = []

    chunk_id = 0

    for document in documents:

        text = document["text"]

        start = 0

        while start < len(text):

            end = min(
                start + CHUNK_SIZE,
                len(text)
            )

            # Preserve word boundaries
            if end < len(text):

                boundary = text.rfind(
                    " ", start, end
                )

                if boundary > start:
                    end = boundary

            chunk_text = text[start:end].strip()

            if chunk_text:

                all_chunks.append({

                    "id": chunk_id,

                    "text": chunk_text,

                    "source": document["source"],

                    "page": document["page"]

                })

                chunk_id += 1

            if end >= len(text):
                break

            start = end - CHUNK_OVERLAP

    print("\nCHUNKING COMPLETED")

    print("Total Chunks:", len(all_chunks))

    return all_chunks


# ==========================================
# 5. COMPLETE PDF PROCESSING
# ==========================================

def process_pdf(pdf_path):

    documents = extract_pdf(pdf_path)

    chunks = split_into_chunks(documents)

    return chunks


# ==========================================
# 6. PROCESS ADDITIONAL UPLOADED PDF
# ==========================================

def process_pdf_bytes(pdf_bytes, filename):

    documents = extract_pdf_bytes(
        pdf_bytes,
        filename
    )

    chunks = split_into_chunks(documents)

    return chunks
