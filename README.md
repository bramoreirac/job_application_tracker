# Job Application Tracker

A private job application tracker built step by step with React and Django. The project is currently a local learning project, not a deployed application. See [plan.md](plan.md) for the full scope and milestones and [guide.md](guide.md) for the hands-on learning workflow.

## Current status

- **Stage 1 complete:** Django REST Framework serves `GET /api/health/`, and the React page fetches it and displays the backend status. Local CORS allows `http://localhost:5173`.
- **Stage 2 complete:** the `applications` app has an `Application` model, an initial migration applied to local SQLite, and a completed synthetic ORM create/filter/update/delete exercise.
- **Stage 3 in progress:** Django registration, token login, current-user, and logout endpoints are implemented with protected API defaults. React has login and registration pages, plus a protected `/applications` route with a signed-in placeholder and logout.
- Registration and login have a shared anonymous throttle of 10 requests per minute. Automated tests cover that limit and the login contract. Local API and browser checks covered registration, login, logout, route redirects, token invalidation, and returning to login after a browser reload. Additional authentication tests remain to be written.
- Application API CRUD and the tracker dashboard, search, filters, hosted PostgreSQL, and deployment are still to be built.

## Stack

| Part | Current choice |
| --- | --- |
| Frontend | React, Vite, JavaScript, React Router |
| Backend | Python, Django 6.1, Django REST Framework |
| Local database | SQLite with the initial application migration |
| Planned hosting | Vercel Hobby, Render Free, Supabase Free PostgreSQL |

## Run locally on Linux

Run the backend and frontend in separate terminals. Python 3.14 and Node.js 22 have been used for local checks. Install the Python virtual-environment package for your distribution if `python3 -m venv` is unavailable.

**Backend terminal:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Replace the placeholder `DJANGO_SECRET_KEY` in `backend/.env` with a newly generated private value. Then run:

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
```

To create an admin account, run `python manage.py createsuperuser` and sign in at `http://127.0.0.1:8000/admin/`. The application model is not yet registered in the admin.

**Frontend terminal:**

```bash
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

Open `http://localhost:5173`. The backend health endpoint is `http://127.0.0.1:8000/api/health/`. For existing setups, keep the existing `.env` and `.env.local` files instead of overwriting them.

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

Anonymous registration and login requests share a limit of 10 per minute per client IP; exceeding it returns 429. The current cache-based throttle is a basic safeguard, not a complete distributed security boundary.

## Repository layout

```text
backend/    Django project, accounts app, and applications app
frontend/   React/Vite client
plan.md     Scope, API contract, and milestones
guide.md    Hands-on learning stages and workflow
```

The root `.gitignore` excludes local secrets, virtual environments, SQLite files, caches, and frontend build output. The `.env.example` files document required local settings without real credentials.
