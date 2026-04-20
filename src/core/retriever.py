"""RAG retriever and generator."""
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from .llm import get_llm
from .prompts import SYSTEM_PROMPT
from .vectorstore import similarity_search_with_relevance
from ..config.settings import settings

ESCALATION_TOKEN = "ESCALAR_HUMANO"
ESCALATION_REASON_NO_CONTEXT = "No se encontro contexto documental suficiente"
ESCALATION_REASON_OUT_OF_SCOPE = "Pregunta fuera de scope de documentos"


def create_rag_chain():
    """Build prompt -> LLM -> parser chain."""
    llm = get_llm()
    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)
    return prompt | llm | StrOutputParser()


def retrieve_relevant_docs(query: str) -> list:
    """Retrieve only docs above the configured relevance threshold."""
    matches = similarity_search_with_relevance(query, k=settings.retrieval_k)
    filtered_docs = []

    for doc, score in matches:
        if score >= settings.retrieval_score_threshold:
            doc.metadata["relevance_score"] = score
            filtered_docs.append(doc)

    return filtered_docs


def format_context(docs: list) -> str:
    """Format retrieved documents into a prompt context block."""
    return "\n\n".join(
        [
            (
                f"Fuente: {doc.metadata.get('source', 'unknown')}\n"
                f"Relevancia: {doc.metadata.get('relevance_score', 0):.2f}\n"
                f"Contenido:\n{doc.page_content}"
            )
            for doc in docs
        ]
    )


def serialize_sources(docs: list) -> list[dict]:
    """Return response-safe source metadata for retrieved docs."""
    serialized = []
    seen = set()

    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        content = doc.page_content
        key = (source, content)
        if key in seen:
            continue
        seen.add(key)
        serialized.append({"source": source, "content": content})

    return serialized


def should_escalate(response: str, sources: list[dict]) -> tuple[bool, str]:
    """Determine whether the answer should be escalated."""
    normalized_response = response.strip().lower()

    if not sources:
        return True, ESCALATION_REASON_NO_CONTEXT

    escalation_markers = [
        ESCALATION_TOKEN.lower(),
        "no tengo información",
        "no tengo informacion",
        "no sé",
        "no se",
        "contacta",
        "no puedo ayudar",
    ]
    if any(marker in normalized_response for marker in escalation_markers):
        return True, ESCALATION_REASON_OUT_OF_SCOPE

    return False, ""


def rag_query(query: str) -> dict:
    """Execute RAG query with stronger out-of-scope handling."""
    docs = retrieve_relevant_docs(query)
    sources = serialize_sources(docs)

    if not docs:
        return {
            "answer": "Escalando a agente humano.",
            "escalate": True,
            "reason": ESCALATION_REASON_NO_CONTEXT,
            "sources": [],
        }

    chain = create_rag_chain()
    response = chain.invoke(
        {
            "question": query,
            "history": "",
            "context": format_context(docs),
        }
    ).strip()

    escalate, reason = should_escalate(response, sources)
    if escalate:
        return {
            "answer": "Escalando a agente humano.",
            "escalate": True,
            "reason": reason,
            "sources": sources,
        }

    return {"answer": response, "escalate": False, "sources": sources}
