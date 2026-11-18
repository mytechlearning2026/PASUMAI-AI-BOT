
import re
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from backend.document_processor import process_pdf_bytes

from backend.vector_store import (
    build_vector_store,
    load_vector_store,
    get_vector_store_status
)

from backend.rag_pipeline import answer_question


# ==========================================
# PASUMAI AI BOT - FASTAPI BACKEND
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "data" / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# INITIALIZE FASTAPI
# ==========================================

app = FastAPI(

    title="PASUMAI AI BOT",

    description=(
        "AI Assistant for Indian Government "
        "Agricultural Schemes"
    ),

    version="1.0.0"

)


# ==========================================
# REQUEST MODEL
# ==========================================

class ChatRequest(BaseModel):

    question: str


# ==========================================
# HELPER: REBUILD KNOWLEDGE BASE
# ==========================================

def update_knowledge_base(new_chunks):

    if not new_chunks:

        raise ValueError("No readable PDF content found.")

    # Load existing chunks if an index already exists

    index_path = BASE_DIR / "data" / "faiss_index" / "index.faiss"

    if index_path.exists():

        _, existing_chunks = load_vector_store()

    else:

        existing_chunks = []

    # Combine existing and new chunks

    combined_chunks = existing_chunks + new_chunks

    # Remove duplicate content

    unique_chunks = {}

    for chunk in combined_chunks:

        key = (
            chunk["source"],
            chunk["page"],
            chunk["text"]
        )

        unique_chunks[key] = chunk

    final_chunks = list(unique_chunks.values())

    # Assign globally unique IDs

    for idx, chunk in enumerate(final_chunks):

        chunk["id"] = idx

    # Rebuild FAISS index

    build_vector_store(final_chunks)

    return len(final_chunks)


# ==========================================
# 1. HEALTH CHECK
# ==========================================

@app.get("/")

def home():

    return {

        "application": "PASUMAI AI BOT",

        "message": "Backend is running successfully!",

        "status": "online"

    }


# ==========================================
# 2. UPLOAD PDF DOCUMENTS
# ==========================================


@app.post("/upload")
async def upload_documents(
    file: UploadFile = File(...)
):

    try:

        if not file.filename.lower().endswith(".pdf"):

            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed."
            )

        safe_name = Path(file.filename).name

        pdf_bytes = await file.read()

        if not pdf_bytes:

            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty."
            )

        # Save uploaded PDF
        save_path = UPLOAD_DIR / safe_name

        save_path.write_bytes(pdf_bytes)

        # Process PDF
        new_chunks = process_pdf_bytes(
            pdf_bytes,
            safe_name
        )

        # Update FAISS database
        total_chunks = update_knowledge_base(
            new_chunks
        )

        return {

            "status": "success",

            "message": "PDF uploaded successfully!",

            "uploaded_file": safe_name,

            "new_chunks": len(new_chunks),

            "total_chunks": total_chunks

        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================
# 3. CHAT ENDPOINT
# ==========================================

@app.post("/chat")

def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        # Execute complete RAG pipeline

        response = answer_question(question)

        return {

            "status": "success",

            "question": response["question"],

            "answer": response["answer"],

            "sources": response["sources"],

            "retrieved_chunks": response["retrieved_chunks"],

            "model": response["model"]

        }

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=503,
            detail=f"Knowledge base is not ready: {str(e)}"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


# ==========================================
# 4. KNOWLEDGE BASE STATUS
# ==========================================

@app.get("/status")

def status():

    try:

        vector_status = get_vector_store_status()

        uploaded_files = [

            file.name

            for file in UPLOAD_DIR.glob("*.pdf")

        ]

        return {

            "application": "PASUMAI AI BOT",

            "vector_database": vector_status,

            "uploaded_documents": uploaded_files,

            "total_uploaded_documents": len(uploaded_files)

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
