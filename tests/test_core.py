"""Core tests."""
import asyncio
import sys
from pathlib import Path
from httpx import ASGITransport, AsyncClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.core.retriever import rag_query
from src.api.app import app
from unittest.mock import patch, Mock


@patch("src.core.retriever.similarity_search")
@patch("src.core.retriever.create_rag_chain")
def test_rag_escalate(mock_chain, mock_search):
    mock_chain.return_value.invoke.return_value = "No tengo información sobre eso. Contacta a un agente humano."
    mock_search.return_value = []
    result = rag_query("clima?")
    assert result["escalate"] is True
    assert result["sources"] == []


@patch("src.core.retriever.similarity_search")
@patch("src.core.retriever.create_rag_chain")
def test_rag_normal(mock_chain, mock_search):
    mock_chain.return_value.invoke.return_value = "Horarios: Lunes 6pm"
    mock_search.return_value = []
    result = rag_query("horarios")
    assert not result["escalate"]

@patch("src.core.retriever.similarity_search")
@patch("src.core.retriever.create_rag_chain")
def test_rag_sources(mock_chain, mock_search):
    mock_chain.return_value.invoke.return_value = "Según el documento horarios.md, abrimos a las 8am."
    mock_search.return_value = [Mock(metadata={"source": "horarios.md"}, page_content="Horarios del nivel A1")]
    result = rag_query("¿A qué hora abren?")
    assert result["sources"] == [{"source": "horarios.md", "content": "Horarios del nivel A1"}]


@patch("src.api.routes.chat.rag_query")
def test_chat_endpoint_success(mock_rag_query):
    mock_rag_query.return_value = {
        "answer": "Según horarios.md, inglés A1 es Lun/Mié 6-8pm.",
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
        "answer": "Según horarios.md, inglés A1 es Lun/Mié 6-8pm.",
        "escalate": False,
        "reason": None,
        "sources": [{"source": "horarios.md", "content": "A1: Lun/Mié 6-8pm"}],
    }


@patch("src.api.routes.chat.rag_query")
def test_chat_endpoint_escalation(mock_rag_query):
    mock_rag_query.return_value = {
        "answer": "Escalando a agente humano.",
        "escalate": True,
        "reason": "Fuera de scope de documentos",
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
        "reason": "Fuera de scope de documentos",
        "sources": [],
    }
