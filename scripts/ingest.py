#!/usr/bin/env python
"""Ingest documents into Chroma vector store."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

from src.data.loaders import load_documents, split_documents
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from src.core.llm import get_embeddings
import os


def main():
    print("Loading documents...")
    documents_path = root / "data" / "documents"
    docs = load_documents(str(documents_path))
    print(f"Loaded {len(docs)} documents")

    print("Splitting into chunks...")
    splits = split_documents(docs)
    print(f"Created {len(splits)} chunks")

    print("Creating embeddings and storing in Chroma...")
    embeddings = get_embeddings()
    Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    print("✅ Ingest complete! Vectorstore ready at ./chroma_db")


if __name__ == "__main__":
    main()
