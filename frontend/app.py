
import os
import requests
import streamlit as st

from pathlib import Path
from dotenv import load_dotenv


# ==========================================
# PASUMAI AI BOT - STREAMLIT FRONTEND
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

API_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000"
)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(

    page_title="PASUMAI AI BOT",

    page_icon="🌱",

    layout="wide",

    initial_sidebar_state="collapsed"

)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.main {
    background-color: #f7faf7;
}

.main-title {
    color: #176b3a;
    font-size: 36px;
    font-weight: bold;
    text-align: center;
}

.sub-title {
    color: #555555;
    font-size: 16px;
    text-align: center;
}

.section-title {
    color: #176b3a;
    font-size: 23px;
    font-weight: bold;
}

.status-box {
    background-color: #e8f5e9;
    padding: 12px;
    border-radius: 10px;
}

div.stButton > button {
    background-color: #198754;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}

div.stButton > button:hover {
    background-color: #146c43;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE
# ==========================================

if "messages" not in st.session_state:

    st.session_state.messages = []


if "uploaded_files" not in st.session_state:

    st.session_state.uploaded_files = []


# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="main-title">🌱 PASUMAI AI BOT</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Your AI Assistant for Indian Government Farmer Schemes'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# BACKEND CONNECTION STATUS
# ==========================================

try:

    health = requests.get(
        f"{API_URL}/",
        timeout=5
    )

    if health.status_code == 200:

        st.success("Backend Connected Successfully")

    else:

        st.error("Backend is not responding correctly.")

except requests.RequestException:

    st.error(
        "Backend is not connected. "
        "Please start FastAPI in another terminal."
    )


# ==========================================
# TWO-COLUMN LAYOUT
# ==========================================

left_col, right_col = st.columns(
    [1, 2],
    gap="large"
)


# ==========================================
# LEFT SIDE - DOCUMENT UPLOAD
# ==========================================

with left_col:

    st.markdown(
        '<div class="section-title">📂 Document Upload</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Upload additional government scheme PDF documents."
    )

    uploaded_pdfs = st.file_uploader(

        "Choose PDF documents",

        type=["pdf"],

        accept_multiple_files=True,

        key="pdf_uploader"

    )

    if st.button(
        "📤 Upload and Process Documents",
        use_container_width=True
    ):

        if not uploaded_pdfs:

            st.warning("Please select at least one PDF.")

        else:

            progress = st.progress(0)

            success_count = 0

            total_files = len(uploaded_pdfs)

            for i, pdf in enumerate(uploaded_pdfs):

                try:

                    files = {

                        "file": (

                            pdf.name,

                            pdf.getvalue(),

                            "application/pdf"

                        )

                    }

                    response = requests.post(

                        f"{API_URL}/upload",

                        files=files,

                        timeout=300

                    )

                    if response.status_code == 200:

                        result = response.json()

                        success_count += 1

                        if pdf.name not in st.session_state.uploaded_files:

                            st.session_state.uploaded_files.append(
                                pdf.name
                            )

                        st.success(
                            f"Processed: {pdf.name}"
                        )

                        st.write(
                            f"New chunks: {result['new_chunks']}"
                        )

                    else:

                        st.error(
                            f"{pdf.name}: {response.text}"
                        )

                except requests.RequestException as e:

                    st.error(
                        f"Upload failed: {pdf.name}: {str(e)}"
                    )

                progress.progress(
                    (i + 1) / total_files
                )

            if success_count > 0:

                st.success(
                    f"{success_count}/{total_files} "
                    "PDF document(s) processed successfully!"
                )

                st.rerun()

    st.divider()

    st.markdown("### 📑 Uploaded Documents")

    if st.session_state.uploaded_files:

        for filename in st.session_state.uploaded_files:

            st.write(f"📄 {filename}")

    else:

        st.info(
            "No additional PDFs uploaded in this session."
        )

    st.divider()

    st.markdown("### 📊 Knowledge Base Status")

    if st.button(
        "Check Database Status",
        use_container_width=True
    ):

        try:

            response = requests.get(
                f"{API_URL}/status",
                timeout=15
            )

            if response.status_code == 200:

                status_data = response.json()

                vector_status = status_data.get(
                    "vector_database", {}
                )

                st.write(
                    "**Vector database:**",
                    vector_status.get("status", "Unknown")
                )

                st.write(
                    "**Total vectors:**",
                    vector_status.get("total_vectors", 0)
                )

                st.write(
                    "**Total chunks:**",
                    vector_status.get("total_chunks", 0)
                )

                st.write(
                    "**Uploaded PDFs:**",
                    status_data.get(
                        "total_uploaded_documents", 0
                    )
                )

            else:

                st.error(response.text)

        except requests.RequestException as e:

            st.error(str(e))


# ==========================================
# RIGHT SIDE - AI CHAT ASSISTANT
# ==========================================

with right_col:

    st.markdown(
        '<div class="section-title">🤖 AI Farmer Assistant</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Ask questions about Indian Government agricultural schemes."
    )

    # Example questions

    with st.expander("💡 Example Questions"):

        example_questions = [

            "What is PM-KISAN?",

            "Who is eligible for PM-KISAN?",

            "How can I apply for a Kisan Credit Card?",

            "What documents are required for PMFBY?",

            "Is there any subsidy for drip irrigation?",

            "What schemes are available for dairy farmers?"

        ]

        for question in example_questions:

            if st.button(
                question,
                key=f"example_{question}"
            ):

                st.session_state.pending_question = question

                st.rerun()

    # Display chat history

    chat_container = st.container()

    with chat_container:

        for message in st.session_state.messages:

            with st.chat_message(message["role"]):

                st.markdown(message["content"])

                if message.get("sources"):

                    with st.expander("📚 View Sources"):

                        for source in message["sources"]:

                            st.write(
                                f"📄 {source['document']} "
                                f"| Page {source['page']}"
                            )

    # Chat input

    prompt = st.chat_input(
        "Ask your question about farmer schemes..."
    )

    pending_question = st.session_state.pop(
        "pending_question",
        None
    )

    user_question = pending_question or prompt

    if user_question:

        # Display user question

        st.session_state.messages.append({

            "role": "user",

            "content": user_question

        })

        with st.chat_message("user"):

            st.markdown(user_question)

        # Generate AI answer

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching government schemes and generating answer..."
            ):

                try:

                    response = requests.post(

                        f"{API_URL}/chat",

                        json={

                            "question": user_question

                        },

                        timeout=180

                    )

                    response.raise_for_status()

                    result = response.json()

                    answer = result["answer"]

                    sources = result.get(
                        "sources", []
                    )

                    st.markdown(answer)

                    if sources:

                        with st.expander("📚 View Sources"):

                            for source in sources:

                                st.write(
                                    f"📄 {source['document']} "
                                    f"| Page {source['page']}"
                                )

                    st.session_state.messages.append({

                        "role": "assistant",

                        "content": answer,

                        "sources": sources

                    })

                except requests.RequestException as e:

                    error_message = (
                        "Unable to connect to the AI backend. "
                        f"Error: {str(e)}"
                    )

                    st.error(error_message)

                    st.session_state.messages.append({

                        "role": "assistant",

                        "content": error_message

                    })


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:gray;">

    🌱 PASUMAI AI BOT

    <br>

    AI-powered Government Scheme Assistant for Indian Farmers

    <br>

    Built using Python | Streamlit | FastAPI | FAISS | BM25 | OpenAI

    </div>
    """,
    unsafe_allow_html=True
)
