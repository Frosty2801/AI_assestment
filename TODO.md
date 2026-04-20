# AI Language Assistant TODO

## Approved Plan Steps (Python/FastAPI/LangChain)

1. ✅ Create TODO.md (current)
2. ✅ Create project structure files: requirements.txt, .env.example, README.md
3. ✅ Create data/documents/ (4 academy docs)
4. ✅ Create src/config/, core/, data/, utils/
5. ✅ Create src/api/
6. ✅ Create scripts/ingest.py, metrics.py
7. ✅ Create n8n-workflow.json
8. Install deps: `pip install -r requirements.txt`
9. Run ingest: `python scripts/ingest.py`
10. Test API: `uvicorn src.api.app:app --reload`, POST /chat queries
11. Import n8n workflow, test end-to-end (Telegram → response/escalate)
12. Add metrics (queries/cost/escalate rate)
13. Finalize README with setup/demo, zip project

Next: Step 2.
