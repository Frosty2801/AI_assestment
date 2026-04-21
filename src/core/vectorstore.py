"""Vector store management with ChromaDB."""
import os

from langchain_chroma import Chroma
from langchain.docstore.document import Document
from chromadb.config import Settings as ChromaSettings
from ..config.settings import settings
from .llm import get_embeddings


def get_chroma_settings(persist_directory: str | None = None) -> ChromaSettings:
    """Disable noisy Chroma telemetry in local development."""
    persist_directory = os.path.abspath(persist_directory or settings.chroma_path)
    return ChromaSettings(
        is_persistent=True,
        persist_directory=persist_directory,
        anonymized_telemetry=False,
        chroma_product_telemetry_impl="src.core.chroma_telemetry.NoOpTelemetryClient",
        chroma_telemetry_impl="src.core.chroma_telemetry.NoOpTelemetryClient",
    )


def get_vectorstore() -> Chroma:
    """Get or create Chroma vector store."""
    chroma_path = os.path.abspath(settings.chroma_path)
    if not os.path.exists(chroma_path):
        raise ValueError(f"Vectorstore not found at {chroma_path}. Run ingest.py first.")
    
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=chroma_path,
        embedding_function=embeddings,
        client_settings=get_chroma_settings(chroma_path),
    )


def similarity_search(query: str, k: int = 5) -> list[Document]:
    """Retrieve top-k relevant chunks."""
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search(query, k=k)


def similarity_search_with_relevance(query: str, k: int = 5) -> list[tuple[Document, float]]:
    """Retrieve top-k chunks with relevance scores."""
    vectorstore = get_vectorstore()
    return vectorstore.similarity_search_with_relevance_scores(query, k=k)
