"""Chat routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ...core.retriever import rag_query
from scripts.metrics import record_query, get_metrics


router = APIRouter()


class ChatRequest(BaseModel):
    query: str


class SourceItem(BaseModel):
    source: str
    content: str


class ChatResponse(BaseModel):
    answer: str
    escalate: bool
    reason: Optional[str] = None
    sources: list[SourceItem] = []


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process user query with RAG."""
    try:
        result = rag_query(request.query)
        cost = 0.001  # placeholder
        record_query(cost, result["escalate"])
        
        if result["escalate"]:
            return ChatResponse(
                answer=result.get("answer", "Escalando a agente humano."),
                escalate=True,
                reason=result.get("reason", "Fuera de scope"),
                sources=result.get("sources", []),
            )
        return ChatResponse(
            answer=result["answer"],
            escalate=False,
            sources=result.get("sources", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def metrics():
    """Get usage metrics."""
    return get_metrics()
