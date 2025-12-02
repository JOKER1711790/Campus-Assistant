## Smart Campus Assistant – MVP

This repository contains a minimal but working skeleton for the **Smart Campus Assistant** MVP:
- **Backend**: FastAPI, async SQLAlchemy, basic RAG stub using sentence-transformers + FAISS.
- **Frontend**: Single-page React UI (via CDN) with Tailwind CSS and a clean chat interface.

### 1. Folder structure

- `backend/`
  - `app/` – FastAPI application
    - `main.py` – FastAPI app + routing
    - `config.py` – settings and environment configuration
    - `db.py` – async SQLAlchemy engine & session
    - `models.py` – database models (timetables, bus, events, faculty, exams, FAQs)
    - `schemas.py` – Pydantic models for API responses & chat payloads
    - `rag.py` – minimal RAG engine + FAISS index handling
    - `routers/core.py` – main REST endpoints and `/api/chat`
  - `requirements.txt` – backend dependencies
- `frontend/`
  - `index.html` – React + Tailwind chat UI (CDN-based)
- `datasets/` – place your CSV/JSON/PDF source data here (to be wired into RAG + DB import scripts)

### 2. Running the backend (dev)

From the `backend` directory:

```bash
cd backend
python -m venv venv  # if you don't already have one
venv\Scripts\activate  # on Windows
pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The FastAPI docs will be available at:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

Key endpoints:

- `GET /api/health` – health check
- `GET /api/timetable` – timetable entries (filters: `program`, `semester`, `section`)
- `GET /api/bus_schedule` – bus routes
- `GET /api/events` – campus events
- `GET /api/faculty_directory` – faculty list
- `POST /api/chat` – chatbot endpoint

For now, tables are auto-created on startup using SQLite (`smart_campus.db`). You can switch to Postgres later by changing `database_url` in `app/config.py`.

### 3. Running the frontend (dev)

The frontend is intentionally very light for the MVP:

```bash
cd frontend
python -m http.server 5173
```

Then open:

- `http://localhost:5173`

The UI will talk to `http://localhost:8000/api/chat` by default. Make sure the backend is running.

### 4. Next steps – plugging in real campus data

1. **Prepare datasets** (CSV/JSON) for:
   - Timetables, bus schedules, events, exam schedules, faculty directory, FAQs.
2. **Write small import scripts** that:
   - Read CSVs from `datasets/`
   - Map rows into ORM models in `app/models.py`
   - Insert into the DB using an `AsyncSession`.
3. **Build the RAG index**:
   - Extract text from PDFs / notices into plain text chunks.
   - Call `RAGEngine.build_index(documents)` with `(text, source_id)` tuples.
   - Persisted FAISS index will then be used automatically by `/api/chat`.

Once those are in place, the MVP will answer queries both via **structured tables** and **retrieved campus documents** from the RAG pipeline.



