# Job Application Tracker

A private job application tracker built step by step with React and Django. The project is currently a local learning project, not a deployed application. See [plan.md](plan.md) for the full scope and milestones.

## Current status

- **Stage 1 complete:** Django REST Framework serves `GET /api/health/`, and the React page fetches it and displays the backend status. Local CORS allows `http://localhost:5173`.
- **Stage 2 complete:** the `applications` app has an `Application` model, an initial migration applied to local SQLite, and a completed synthetic ORM create/filter/update/delete exercise.
- **Stage 3 in progress:** Django registration, token login, current-user, and logout endpoints are implemented with protected API defaults. React has login and registration pages, plus a protected `/applications` route with a signed-in placeholder and logout.
- Local API and browser checks covered registration, login, logout, route redirects, and token invalidation. Focused automated tests cover the login contract. Browser reload behavior, additional authentication tests, and authentication throttling remain to be verified or implemented.
- Application API CRUD and the tracker dashboard, search, filters, hosted PostgreSQL, and deployment are still to be built.

## Stack

| Part | Current choice |
| --- | --- |
| Frontend | React, Vite, JavaScript, React Router |
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

Open `http://localhost:5173`. The page should show **Backend status: ok** and redirect to the sign-in form. Use **Create an account** to register a local user, then return to sign in. The protected applications page currently shows a signed-in message and logout button; job tracking is not implemented yet. The example Vite variable contains only the public API address; never put a database password or authentication token in a `VITE_` variable. If PowerShell blocks `npm.ps1`, use `npm.cmd ci` and `npm.cmd run dev`.

## Current authentication API

| Method | Endpoint | Current behavior |
| --- | --- | --- |
| GET | `/api/health/` | Public health response |
| POST | `/api/auth/register/` | Validates username, optional email, password and confirmation; creates a user and returns public user fields with 201 |
| POST | `/api/auth/login/` | Returns `{token, user}` with 200, or a generic 401 for invalid credentials |
| GET | `/api/auth/me/` | Returns the authenticated user's public fields; missing or invalid token returns 401 |
| POST | `/api/auth/logout/` | Deletes the token and returns an empty 204 |

Protected requests use `Authorization: Token <value>`. The React client holds the token in memory, so a full reload requires another login. Reloading does not revoke the server token; logout does. DRF's standard token has no automatic expiry and is shared across a user's sessions, so logout invalidates it for those sessions too.

## Repository layout

```text
backend/    Django project, accounts app, and applications app
frontend/   React/Vite client
plan.md     Scope, API contract, and milestones
```

The root `.gitignore` excludes local secrets, virtual environments, SQLite files, caches, and frontend build output. The `.env.example` files document required local settings without real credentials.
