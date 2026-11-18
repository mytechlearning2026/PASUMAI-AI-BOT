
from backend.rag_pipeline import answer_question


# ==========================================
# PASUMAI AI BOT - OPENAI RAG TEST
# ==========================================

print("\n================================")

print("PASUMAI AI BOT")

print("OPENAI RAG TEST")

print("================================")


# Ask a question

question = (
    "What is PM-KISAN? "
    "Who is eligible and what benefits "
    "are available?"
)


try:

    # Run complete RAG pipeline

    response = answer_question(question)

    # Display answer

    print("\nQUESTION:")

    print(response["question"])

    print("\nCHATGPT ANSWER:")

    print(response["answer"])

    # Display sources

    print("\nSOURCE REFERENCES:")

    for source in response["sources"]:

        print(
            f"Document: {source['document']} "
            f"| Page: {source['page']}"
        )

    print(
        "\nRetrieved chunks:",
        response["retrieved_chunks"]
    )

    print(
        "Model:",
        response["model"]
    )

    print("\nOPENAI RAG TEST SUCCESSFUL!")


except Exception as e:

    print("\nERROR OCCURRED:")

    print(str(e))
