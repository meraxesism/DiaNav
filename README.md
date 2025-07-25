# DiaNav GenAI Backend

This is a FastAPI backend for DiaNav, an AI assistant for automotive diagnostics using structured DTC data.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the backend:

```bash
uvicorn dianav_backend:app --reload
```

3. Query the API:
- Health check: [GET] http://localhost:8000/health
- Query: [POST] http://localhost:8000/query
  - JSON body: `{ "query": "What causes B1087?" }`

## Data
- Place your `.txt` and `.json` files in the project root (as in this example).

## Next Steps
- Integrate OpenAI or other LLM for advanced conversational responses.
- Add frontend chat UI if desired. 