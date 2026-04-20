"""Core tests."""
import asyncio
import sys
from pathlib import Path
from httpx import ASGITransport, AsyncClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.api.app import app
from src.core.retriever import (
    ESCALATION_REASON_NO_CONTEXT,
    ESCALATION_REASON_OUT_OF_SCOPE,
    rag_query,
)
from unittest.mock import Mock, patch


def make_doc(source: str, content: str, relevance: float = 0.8) -> Mock:
    """Build a mock document with metadata."""
    return Mock(metadata={"source": source, "relevance_score": relevance}, page_content=content)


@patch("src.core.retriever.similarity_search_with_relevance")
def test_rag_escalate_without_context(mock_search):
    mock_search.return_value = []
    result = rag_query("clima?")
    assert result["escalate"] is True
    assert result["reason"] == ESCALATION_REASON_NO_CONTEXT
    assert result["sources"] == []


@patch("src.core.retriever.similarity_search_with_relevance")
@patch("src.core.retriever.create_rag_chain")
def test_rag_normal(mock_chain, mock_search):
    mock_chain.return_value.invoke.return_value = "Segun horarios.md, inglés A1 tiene clases lunes y miércoles de 6-8pm."
    mock_search.return_value = [(make_doc("horarios.md", "A1: Lun/Mié 6-8pm"), 0.91)]

    result = rag_query("horarios")

    assert result["escalate"] is False
    assert "Segun horarios.md" in result["answer"]


@patch("src.core.retriever.similarity_search_with_relevance")
@patch("src.core.retriever.create_rag_chain")
def test_rag_sources(mock_chain, mock_search):
    mock_chain.return_value.invoke.return_value = "Segun horarios.md, abrimos a las 8am."
    mock_search.return_value = [(make_doc("horarios.md", "Horarios del nivel A1"), 0.88)]

    result = rag_query("¿A qué hora abren?")

    assert result["sources"] == [{"source": "horarios.md", "content": "Horarios del nivel A1"}]


@patch("src.core.retriever.similarity_search_with_relevance")
@patch("src.core.retriever.create_rag_chain")
def test_rag_escalates_when_model_returns_escalation_token(mock_chain, mock_search):
    mock_chain.return_value.invoke.return_value = "ESCALAR_HUMANO"
    mock_search.return_value = [(make_doc("horarios.md", "A1: Lun/Mié 6-8pm"), 0.88)]

    result = rag_query("¿Cómo está el tráfico?")

    assert result["escalate"] is True
    assert result["reason"] == ESCALATION_REASON_OUT_OF_SCOPE


@patch("src.api.routes.chat.rag_query")
def test_chat_endpoint_success(mock_rag_query):
    mock_rag_query.return_value = {
        "answer": "Segun horarios.md, inglés A1 es Lun/Mié 6-8pm.",
        "escalate": False,
        "sources": [{"source": "horarios.md", "content": "A1: Lun/Mié 6-8pm"}],
    }

    async def run_test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/chat/", json={"query": "Horarios de inglés A1"})

    response = asyncio.run(run_test())

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Segun horarios.md, inglés A1 es Lun/Mié 6-8pm.",
        "escalate": False,
        "reason": None,
        "sources": [{"source": "horarios.md", "content": "A1: Lun/Mié 6-8pm"}],
    }


@patch("src.api.routes.chat.rag_query")
def test_chat_endpoint_escalation(mock_rag_query):
    mock_rag_query.return_value = {
        "answer": "Escalando a agente humano.",
        "escalate": True,
        "reason": ESCALATION_REASON_OUT_OF_SCOPE,
        "sources": [],
    }

    async def run_test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post("/chat/", json={"query": "¿Cómo está el clima?"})

    response = asyncio.run(run_test())

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Escalando a agente humano.",
        "escalate": True,
        "reason": ESCALATION_REASON_OUT_OF_SCOPE,
        "sources": [],
    }
