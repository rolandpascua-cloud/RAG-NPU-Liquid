#!/usr/bin/env python3
"""
Ingest documents into a FAISS vector store.
Usage: python ingest.py
"""

import os
import sys
from pathlib import Path

from langchain.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

from config import (
    DOCS_DIR,
    VECTORSTORE_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDINGS_MODEL,
)


def ingest():
    """Load documents, chunk, embed, and save to FAISS index."""

    docs_path = Path(DOCS_DIR)
    if not docs_path.exists():
        print(f"✓ Creating {DOCS_DIR}/")
        docs_path.mkdir(parents=True, exist_ok=True)

    # Load documents (txt, pdf, md)
    print(f"📂 Loading documents from {DOCS_DIR}/...")
    loaders = [
        ("*.txt", TextLoader),
        ("*.pdf", PyPDFLoader),
        ("*.md", TextLoader),
    ]

    all_docs = []
    for pattern, loader_cls in loaders:
        try:
            loader = DirectoryLoader(DOCS_DIR, glob=pattern, loader_cls=loader_cls)
            docs = loader.load()
            if docs:
                print(f"  ✓ Found {len(docs)} {pattern} document(s)")
                all_docs.extend(docs)
        except Exception as e:
            print(f"  ⚠ Error loading {pattern}: {e}")

    if not all_docs:
        print("⚠ No documents found in ./docs/. Add .txt, .pdf, or .md files and try again.")
        sys.exit(1)

    print(f"✓ Total documents loaded: {len(all_docs)}")

    # Split documents
    print(f"✂️  Splitting documents (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(all_docs)
    print(f"✓ Created {len(chunks)} chunks")

    # Embed with sentence-transformers
    print(f"🧠 Creating embeddings ({EMBEDDINGS_MODEL})...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)

    # Create and save FAISS index
    print(f"💾 Saving FAISS index to {VECTORSTORE_PATH}...")
    vectorstore_path = Path(VECTORSTORE_PATH)
    vectorstore_path.parent.mkdir(parents=True, exist_ok=True)

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"✓ Index saved: {VECTORSTORE_PATH}")

    print("\n✅ Ingestion complete!")
    print(f"  Documents: {len(all_docs)}")
    print(f"  Chunks: {len(chunks)}")
    print(f"  Embedding model: {EMBEDDINGS_MODEL}")


if __name__ == "__main__":
    ingest()
