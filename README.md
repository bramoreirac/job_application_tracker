# Job Application Tracker

A private job application tracker built step by step with React and Django. The project is currently a local learning project, not a deployed application. See [plan.md](plan.md) for the full scope and milestones.

## Current status

- **Stage 1 complete:** Django REST Framework serves `GET /api/health/`, and the React page fetches it and displays the backend status. Local CORS allows `http://localhost:5173`.
- **Stage 2 complete:** the `applications` app has an `Application` model, an initial migration applied to local SQLite, and a completed synthetic ORM create/filter/update/delete exercise.
- **Stage 3 next:** authentication has not been implemented. Application API CRUD, search, filters, tests, hosted PostgreSQL, and deployment are also pending.

## Stack

| Part | Current choice |
| --- | --- |
| Frontend | React, Vite, JavaScript |
| Backend | Python, Django 5.2, Django REST Framework |
| Local database | SQLite with the initial application migration |
| Planned hosting | Vercel Hobby, Render Free, Supabase Free PostgreSQL |

## Run locally on Windows PowerShell

The project was developed with Python 3.14 and Node.js 24. Run the backend and frontend in separate terminals.

**Backend terminal, from `backend/`:**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Replace the placeholder `DJANGO_SECRET_KEY` in `backend/.env` with a newly generated private value. Do not commit or share `.env`. Then start Django:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/api/health/` to see `{"status":"ok"}`. `migrate` creates the local database tables from the committed migrations; local SQLite data is not committed.

**Frontend terminal, from `frontend/`:**

```powershell
npm ci
Copy-Item .env.example .env.local
npm run dev
```

Open `http://localhost:5173`. The page should show **Backend status: ok**. The example Vite variable contains only the public API address; never put a database password or authentication token in a `VITE_` variable.

## Repository layout

```text
backend/    Django project and applications app
frontend/   React/Vite client
plan.md     Scope, API contract, and milestones
```

The root `.gitignore` excludes local secrets, virtual environments, SQLite files, caches, and frontend build output. The `.env.example` files document required local settings without real credentials.
