
# PASUMAI AI BOT

### AI Assistant for Indian Government Farmer Schemes

## Project Description

PASUMAI AI BOT is a Retrieval Augmented Generation
(RAG) application designed to help Indian farmers
understand Central Government agricultural schemes.

It uses government scheme PDF documents as its
knowledge base and provides answers through an
AI-powered conversational interface.

## Technologies Used

- Python
- Streamlit
- FastAPI
- FAISS
- BM25
- CrossEncoder
- Sentence Transformers
- OpenAI API
- PyPDF

## Architecture

1. PDF Document Processing
2. Text Chunking
3. Embedding Generation
4. FAISS Vector Database
5. BM25 Keyword Retrieval
6. Hybrid Retrieval
7. CrossEncoder Reranking
8. OpenAI Answer Generation
9. Streamlit User Interface

## Installation

Create virtual environment:

python -m venv venv

Activate:

Windows PowerShell:

.\venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

## API Configuration

Create a .env file:

OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4.1-mini

## Run Backend

uvicorn backend.main:app --reload

## Run Frontend

streamlit run frontend/app.py

## Access Application

Streamlit:

http://localhost:8501

FastAPI:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

## Main Features

- Government scheme PDF knowledge base
- Additional PDF upload
- Hybrid BM25 and FAISS retrieval
- CrossEncoder reranking
- OpenAI-powered question answering
- Source document references
- Conversational interface

## Important Note

Answers are based on the available uploaded
documents. Farmers should verify changing
benefits, eligibility and deadlines through
official government sources.
