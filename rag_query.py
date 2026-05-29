#!/usr/bin/env python3
"""
Query the RAG pipeline with FastFlowLM backend.
Usage: python rag_query.py
"""

import sys
import socket
from pathlib import Path
from urllib.parse import urlparse

from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from config import (
    FLM_BASE_URL,
    FLM_MODEL,
    MAX_CONTEXT_TOKENS,
    NUM_PREDICT,
    TEMPERATURE,
    VECTORSTORE_PATH,
    EMBEDDINGS_MODEL,
    RETRIEVAL_K,
    RAG_PROMPT_TEMPLATE,
)


def load_vectorstore():
    """Load FAISS vectorstore."""
    vectorstore_path = Path(VECTORSTORE_PATH)
    if not vectorstore_path.exists():
        print(f"❌ Error: FAISS index not found at {VECTORSTORE_PATH}")
        print("   Run 'python ingest.py' first to create the index.")
        sys.exit(1)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)
    vectorstore = FAISS.load_local(
        VECTORSTORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return vectorstore


def build_rag_chain():
    """Build the RAG chain with FastFlowLM backend."""

    # Load vectorstore
    print("📚 Loading vectorstore...")
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVAL_K})

    # Initialize LLM (FastFlowLM via OpenAI-compatible endpoint)
    print(f"🤖 Connecting to FastFlowLM at {FLM_BASE_URL}...")
    llm = ChatOpenAI(
        model_name=FLM_MODEL,
        openai_api_base=FLM_BASE_URL,
        openai_api_key="no-key",
        max_tokens=NUM_PREDICT,
        temperature=TEMPERATURE,
    )

    # Create prompt template
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=RAG_PROMPT_TEMPLATE,
    )

    # Build RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )

    return qa_chain


def query(qa_chain, question: str) -> dict:
    """Execute a single query and return answer + sources."""
    print(f"\n❓ Question: {question}")
    print("🔍 Retrieving context and generating answer...")

    result = qa_chain.invoke({"query": question})

    answer = result.get("result", "")
    sources = result.get("source_documents", [])

    return {
        "answer": answer,
        "sources": sources,
    }


def main():
    """Interactive CLI for RAG queries."""
    print("=" * 80)
    print("🚀 RAG Pipeline - FastFlowLM + FAISS")
    print("=" * 80)
    print(f"LLM: {FLM_MODEL} @ {FLM_BASE_URL}")
    print(f"Max context: {MAX_CONTEXT_TOKENS} tokens")
    print(f"Retrieval: top-{RETRIEVAL_K} chunks")
    print(f"Vectorstore: {VECTORSTORE_PATH}")
    print("=" * 80)

    # Ensure FastFlowLM is running
    _parsed = urlparse(FLM_BASE_URL)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((_parsed.hostname, _parsed.port))
    sock.close()
    if result != 0:
        print(f"❌ Error: Cannot connect to FastFlowLM at {_parsed.hostname}:{_parsed.port}")
        print(f"   Run 'flm serve {FLM_MODEL}' in a separate terminal first.")
        sys.exit(1)

    print("✅ FastFlowLM is running\n")

    # Build chain
    qa_chain = build_rag_chain()
    print("✅ RAG pipeline ready\n")

    # Interactive loop
    while True:
        try:
            question = input("Enter your question (or 'quit' to exit): ").strip()
            if not question:
                continue
            if question.lower() in ("quit", "exit", "q"):
                print("\nGoodbye!")
                break

            result = query(qa_chain, question)

            print(f"\n✅ Answer:\n{result['answer']}")

            if result["sources"]:
                print(f"\n📄 Sources ({len(result['sources'])} chunks retrieved):")
                for i, doc in enumerate(result["sources"], 1):
                    print(f"\n--- Source {i} ---")
                    print(doc.page_content[:300] + ("..." if len(doc.page_content) > 300 else ""))

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
