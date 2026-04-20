"""Vector store management with ChromaDB."""
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from ..config.settings import settings
from .llm import get_embeddings
import os


def get_vectorstore() -> Chroma:
    """Get or create Chroma vector store."""
    chroma_path = settings.chroma_path
    if not os.path.exists(chroma_path):
        raise ValueError(f"Vectorstore not found at {chroma_path}. Run ingest.py first.")
    
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=chroma_path,
        embedding_function=embeddings
    )


def similarity_search(query: str, k: int = 5) -> list[Document]:
    """Retrieve top-k relevant chunks."""
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search(query, k=k)
