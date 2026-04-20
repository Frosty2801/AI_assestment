"""Ollama LLM client."""
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from ..config.settings import settings


def get_llm(model: str = None, temperature: float = 0.1):
    """Returns configured Ollama LLM."""
    model = model or settings.ollama_model
    return OllamaLLM(
        model=model,
        base_url=settings.ollama_base_url,
        temperature=temperature,
    )


def get_embeddings(model: str = None):
    """Returns Ollama embeddings."""
    model = model or settings.ollama_embedding_model
    return OllamaEmbeddings(
        model=model,
        base_url=settings.ollama_base_url,
    )
