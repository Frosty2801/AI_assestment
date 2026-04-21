# AI Language Assistant

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688)](https://fastapi.tiangolo.com/)
[![n8n](https://img.shields.io/badge/n8n-workflow-ef6d5a)](https://n8n.io/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

RAG assistant for a language academy built with Python, FastAPI, LangChain, Ollama, Chroma, and `n8n`. It answers only from internal business documents about schedules, pricing, levels, and enrollment, and escalates out-of-scope requests to a human.

## ✨ Features

- `POST /chat/` API for document-grounded question answering
- RAG pipeline with chunking, overlap, embeddings, and Chroma persistence
- 4 academy knowledge documents under `data/documents/`
- `n8n` workflow that receives a webhook request, calls FastAPI, and routes escalations
- Prompt with role, constraints, and few-shot examples
- Basic in-memory metrics for query volume, cost estimate, and escalation rate
- Unit tests for RAG behavior and API response contract

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [n8n Workflow](#-n8n-workflow)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Known Limitations](#-known-limitations)
- [Contributing](#-contributing)
- [License](#-license)

## 🏗️ Architecture

1. A user sends a question through an `n8n` webhook or directly to FastAPI.
2. The API retrieves relevant chunks from Chroma using Ollama embeddings.
3. LangChain builds the final prompt with retrieved context.
4. Ollama generates a grounded answer.
5. If the answer indicates the question is outside the business-document scope, the workflow escalates it to a human.

Core components:

- [src/api/app.py](/home/cohorte5/Escritorio/AI_assestment/src/api/app.py:1): FastAPI app and routes
- [src/api/routes/chat.py](/home/cohorte5/Escritorio/AI_assestment/src/api/routes/chat.py:1): `/chat/` and `/chat/metrics`
- [src/core/retriever.py](/home/cohorte5/Escritorio/AI_assestment/src/core/retriever.py:1): RAG orchestration and source serialization
- [src/core/llm.py](/home/cohorte5/Escritorio/AI_assestment/src/core/llm.py:1): Ollama LLM and embedding clients
- [src/core/vectorstore.py](/home/cohorte5/Escritorio/AI_assestment/src/core/vectorstore.py:1): Chroma loading and similarity search
- [scripts/ingest.py](/home/cohorte5/Escritorio/AI_assestment/scripts/ingest.py:1): document ingestion
- [Academy Assistant - Webhook RAG Escalation (1).json](/home/cohorte5/Escritorio/AI_assestment/Academy Assistant - Webhook RAG Escalation (1).json): automation flow

## ✅ Prerequisites

- Python `3.10+`
- `pip`
- [Ollama](https://ollama.com/) installed locally
- `n8n` running locally or in Docker

## 🚀 Quick Start

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd AI_assestment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Update `.env` with values that match your machine and models.

Example:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
N8N_WEBHOOK_SECRET=secret123
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
CHROMA_PATH=./chroma_db
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/slack/webhook
```

> [!WARNING]
> Do not commit a real `.env` file. Store secrets locally only.

### 3. Pull local Ollama models

Choose a model that fits your machine memory. On lower-RAM machines, use a small model.

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

If needed, update `.env` to match the pulled model.

### 4. Ingest the academy documents

```bash
venv/bin/python scripts/ingest.py
```

This loads files from `data/documents/`, splits them into chunks with overlap, generates embeddings, and stores the vectors in `chroma_db/`.

### 5. Start the API

```bash
venv/bin/uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

Open:

- `http://localhost:8000/docs`
- `http://localhost:8000/health`

## ⚙️ Configuration

Environment variables used by the project:

| Variable | Description |
| --- | --- |
| `OLLAMA_BASE_URL` | Base URL for Ollama |
| `OLLAMA_MODEL` | Chat model used for generation |
| `OLLAMA_EMBEDDING_MODEL` | Embedding model used for Chroma retrieval |
| `N8N_WEBHOOK_SECRET` | Optional secret shared with `n8n` |
| `TELEGRAM_BOT_TOKEN` | Present in settings, not required for the current webhook workflow |
| `CHROMA_PATH` | Local path to the vector store |
| `SLACK_WEBHOOK_URL` | Optional webhook for escalation notifications |

## 🔧 Usage

### Query the API directly

```bash
curl -X POST http://127.0.0.1:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"query":"¿Cuáles son los horarios de inglés A1?"}'
```

Example response:

```json
{
  "answer": "Los horarios para inglés principiante son lunes y miércoles de 6-8pm y sábados de 9-11am.",
  "escalate": false,
  "reason": null,
  "sources": [
    {
      "source": "data/documents/horarios.md",
      "content": "# Horarios Academia Idiomas..."
    }
  ]
}
```

### Check service health

```bash
curl http://127.0.0.1:8000/health
```

### Read in-memory metrics

```bash
curl http://127.0.0.1:8000/chat/metrics
```

## 🔄 n8n Workflow

The provided workflow uses a webhook as the entrypoint and your FastAPI service as the AI backend.

### Workflow behavior

1. Receives a POST request with `query`, `message`, or `text`
2. Normalizes the input
3. Calls `POST /chat/`
4. If `escalate=true` or the backend fails, routes to human escalation
5. Returns a structured JSON response to the caller

### Import and configure

1. Import [n8n-workflow.json](/home/cohorte5/Escritorio/AI_assestment/n8n-workflow.json:1) into `n8n`
2. Open the `Ask FastAPI RAG` node
3. Set the URL to one of these:

If `n8n` runs on the same machine:

```text
http://127.0.0.1:8000/chat/
```

If `n8n` runs in Docker and FastAPI runs on your host:

```text
http://host.docker.internal:8000/chat/
```

4. Send a test request:

```bash
curl -X POST "http://localhost:5678/webhook/academy-assistant" \
  -H "Content-Type: application/json" \
  -d '{"query":"¿Cuáles son los horarios de inglés A1?"}'
```

## 📖 API Reference

### `POST /chat/`

Answers a business question using RAG over the ingested documents.

Request body:

```json
{
  "query": "¿Cuáles son los horarios de inglés A1?"
}
```

Response fields:

| Field | Type | Description |
| --- | --- | --- |
| `answer` | `string` | Final answer shown to the user |
| `escalate` | `boolean` | Whether the question should be escalated |
| `reason` | `string \| null` | Escalation reason when applicable |
| `sources` | `array` | Retrieved supporting chunks |

### `GET /chat/metrics`

Returns in-memory usage metrics from [scripts/metrics.py](/home/cohorte5/Escritorio/AI_assestment/scripts/metrics.py:1).

### `GET /health`

Returns API health status.

## 🧪 Testing

Run the test suite with:

```bash
venv/bin/pytest -q
```

Current tests cover:

- normal RAG responses
- escalation detection
- source serialization
- `/chat/` response contract

## 📁 Project Structure

```text
.
├── data/documents/        # Academy business documents
├── scripts/               # Ingestion and metrics helpers
├── src/api/               # FastAPI app and routes
├── src/config/            # Settings and environment loading
├── src/core/              # RAG, prompts, vector store, model clients
├── tests/                 # Unit tests
├── chroma_db/             # Local vector store generated after ingest
└── n8n-workflow.json      # Automation workflow
```

## ⚠️ Known Limitations

- The current implementation uses Ollama locally instead of the OpenAI Responses API
- Escalation detection is based on simple response keywords and can be improved
- Metrics are stored in memory and reset when the API restarts
- Model choice depends on available machine RAM

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a branch: `git checkout -b feature/my-change`
3. Commit your changes: `git commit -m "feat: improve workflow"`
4. Push the branch
5. Open a Pull Request

## 📄 License

MIT
