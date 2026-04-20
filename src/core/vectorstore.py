"""Vector store management with ChromaDB."""
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from chromadb.config import Settings as ChromaSettings
from ..config.settings import settings
from .llm import get_embeddings
import os


def get_chroma_settings() -> ChromaSettings:
    """Disable noisy Chroma telemetry in local development."""
    return ChromaSettings(anonymized_telemetry=False)


def get_vectorstore() -> Chroma:
    """Get or create Chroma vector store."""
    chroma_path = settings.chroma_path
    if not os.path.exists(chroma_path):
        raise ValueError(f"Vectorstore not found at {chroma_path}. Run ingest.py first.")
    
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=chroma_path,
        embedding_function=embeddings,
        client_settings=get_chroma_settings(),
    )


def similarity_search(query: str, k: int = 5) -> list[Document]:
    """Retrieve top-k relevant chunks."""
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search(query, k=k)


def similarity_search_with_relevance(query: str, k: int = 5) -> list[tuple[Document, float]]:
    """Retrieve top-k chunks with relevance scores."""
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search_with_relevance_scores(query, k=k)
