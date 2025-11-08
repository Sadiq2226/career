# Agentic AI Insights Generator for Career Outcomes & Post-Graduation Support

An end-to-end, agentic AI application that analyzes, interprets, and visualizes career outcomes, employment rates, and post‑graduation support insights. Built with FastAPI + LangChain + Streamlit. Runs with or without LLM API keys (graceful offline fallback using extractive heuristics).

## Features
- Agentic analysis over structured CSV/JSON data and unstructured reports
- Endpoints: `/analyze`, `/insights`, `/compare`, `/support-services`
- Streamlit UI with tabs: Career Outcomes, Employment Insights, Support Tools, Compare Institutions
- Visualizations with Plotly/Altair
- Offline mode: heuristic summarizer + TF‑IDF/BM25 retrieval; Online mode: LangChain with LLMs/embeddings

## Quickstart

### 1) Clone and setup
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # Windows
```

### 2) Environment variables (optional for online LLMs)
Edit `.env` and set any you have:
```
OPENAI_API_KEY=
GOOGLE_API_KEY=
HUGGINGFACEHUB_API_TOKEN=
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
```
Without keys, the app runs in offline fallback mode.

### 3) Run backend API
```bash
uvicorn backend.main:app --reload --port 8000
```

### 4) Run Streamlit UI
```bash
streamlit run ui/app.py --server.port 8501
```

Open `http://localhost:8501`

## Project Structure
```
backend/
  main.py
  agent/
    __init__.py
    config.py
    data_loader.py
    chains.py
    service.py
  data/
    employment.csv
    salary.csv
    support_services.json
    reports/
      engineering_2024.txt
      general_support.txt
ui/
  app.py
.env.example
requirements.txt
README.md
```

## Notes
- Data is mock/demo. Replace files in `backend/data/` with your datasets.
- For production, secure your API and configure CORS.
- To use Gemini or OpenAI, set the corresponding keys and models in `.env`.
