"""RAG retriever and generator."""
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from .llm import get_llm
from .prompts import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES
from .vectorstore import similarity_search


SYSTEM_PROMPT_FULL = SYSTEM_PROMPT + FEW_SHOT_EXAMPLES


def create_rag_chain():
    """Build RAG chain: retrieve → format → LLM → parse."""
    llm = get_llm()
    prompt = PromptTemplate.from_template(SYSTEM_PROMPT_FULL)

    def retrieve_docs(inputs: dict) -> str:
        query = inputs["question"]
        docs = similarity_search(query)
        return "\n\n".join([f"Doc: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}" for doc in docs])

    chain = (
        RunnablePassthrough.assign(context=retrieve_docs)
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


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


def rag_query(query: str) -> dict:
    """Execute RAG query, detect escalation."""
    chain = create_rag_chain()
    response = chain.invoke({"question": query, "history": ""}).strip()

    # Retrieve sources for the final response
    docs = similarity_search(query)
    sources = serialize_sources(docs)

    # Simple escalation detection
    escalate_keywords = ["no tengo información", "no sé", "contacta", "no puedo ayudar", "@admin_academia"]
    if any(keyword in response.lower() for keyword in escalate_keywords):
        return {
            "answer": "Escalando a agente humano.",
            "escalate": True,
            "reason": "Fuera de scope de documentos",
            "sources": sources,
        }

    return {"answer": response, "escalate": False, "sources": sources}
