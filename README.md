# CertiFlow — Bulk Certificate Generator

A simple, polished FastAPI backend that generates PDF certificates for many recipients in one request.

## Stack

- FastAPI
- SQLite + SQLAlchemy
- ReportLab
- Pydantic
- Pytest

## Design

The API uses FastAPI BackgroundTasks. A POST request creates a job and immediately returns a job ID. The background task generates certificates one recipient at a time.

Each recipient is independent: if one PDF fails, that recipient is marked `failed` and the remaining recipients continue.

SQLite keeps setup simple. Generated PDFs are stored in `certificates/`.

## Setup — Windows PowerShell

```powershell
cd C:\path\to\bulk_certificate_generator
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If activation is blocked:

```powershell
venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
python -m uvicorn app.main:app --reload
```

Open Swagger:

http://127.0.0.1:8000/docs

## Create a job

POST `/jobs`

```json
{
  "event_name": "AI & Innovation Workshop",
  "event_date": "October 07, 2026",
  "issuer": "FutureTech Academy",
  "recipients": [
    {
      "name": "Aarav Kumar",
      "email": "aarav@example.com",
      "achievement": "for successfully completing the AI & Innovation Workshop"
    },
    {
      "name": "Meera Shah",
      "email": "meera@example.com",
      "achievement": "for successfully completing the AI & Innovation Workshop"
    }
  ]
}
```

The response contains a `job_id`.

## Check status

GET `/jobs/{job_id}`

The response contains:

- total
- completed
- successful
- failed
- progress_percent
- result for every recipient

Job status is one of:

- `queued`
- `processing`
- `completed`
- `completed_with_errors`

## Download

GET `/certificates/{recipient_id}/download`

Only successfully generated certificates can be downloaded.

## Test

```powershell
python -m pytest -q
```

Tests cover:

1. job creation
2. input validation
3. PDF generation
4. job progress
5. individual failure handling
6. certificate retrieval

## Interview explanation

### Why background processing?
Bulk generation may involve hundreds of PDFs. Returning immediately with a job ID keeps the API responsive. For a much larger production system, the same service could be moved to Celery/RQ or another queue.

### Why SQLite?
It satisfies the relational database requirement without requiring PostgreSQL installation. SQLAlchemy keeps the database layer replaceable.

### Why one certificate failure does not stop the job
The service wraps each recipient's generation in its own `try/except`. A failure is saved against that recipient while the loop continues.

### Why ReportLab?
It is lightweight, Python-native, and makes a fixed certificate template easy to generate without requiring a browser.

## Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/jobs` | Start bulk generation |
| GET | `/jobs/{job_id}` | Track progress |
| GET | `/certificates/{recipient_id}/download` | Download PDF |
