# Job Application Tracker — Django Project Plan

## Purpose and learning goal

Build a private tracker for job opportunities and applications. Practice Python backend development with Django, a REST API, authentication, relational modeling, and online deployment. The user has completed a React/Vite/Express task tracker; this project should teach what changes when Express is replaced by Django.

Read guide.md before implementation. It controls the learning workflow: one stage at a time, leave key backend code and first deployment actions to the user, review results, then wait. Codex may handle React UI and repetitive scaffolding when asked. Do not generate the whole backend at once. Keep these files in the new project's root; do not overwrite the completed task tracker.

## Stack and zero-cost requirement

| Layer | Choice | Role |
|---|---|---|
| Frontend | React + Vite, JavaScript, React Router | Responsive login, forms, list and filters |
| Backend | Python + Django + Django REST Framework (DRF) | Users, validation, REST endpoints, business logic |
| Persistence | Django ORM and Django migrations | Model/query/version database schema |
| Authentication | Django users + DRF TokenAuthentication | Password hashing and protected API requests |
| Local database | SQLite initially | Fast local learning with no hosted credentials |
| Deployed database | Supabase Free PostgreSQL | Durable relational storage, accessed only by Django |
| Frontend hosting | Vercel Hobby | Personal noncommercial learning deployment |
| Backend hosting | Render Free, Gunicorn WSGI | Run Python backend over HTTPS |

Use a currently supported Django LTS release compatible with the chosen Python/DRF versions; verify official compatibility before installing. Pin resolved Python dependency versions and commit the frontend lockfile. Typical supporting packages: django-cors-headers, dj-database-url, psycopg with a compatible install option, python-dotenv, Gunicorn, and WhiteNoise for admin/static assets. Do not add packages without explaining their purpose.

Use only free tiers. No paid instances, billable upgrades/add-ons, auto-converting trials, or purchased domains. Verify account eligibility, free project quotas, and current limits before provisioning. The previous project may already use account quotas; do not delete or reuse its data without authorization. Render Free databases are not selected: use Supabase Free PostgreSQL instead. If a free quota blocks progress, report the blocker and discuss a free alternative. Do not silently change stack or upgrade.

## MVP scope

The first screen is login. A user can register, sign in, save job records, update them, filter them, and delete them. Each user sees only their own records. Support saved opportunities that have not yet been applied to.

Required views: /login, /register, /applications. Dashboard includes add/edit form, compact table or mobile cards, status filter, text search, simple counts, loading/empty/error states, and logout. Readable on phone and desktop. Confirm before deleting a record.

Defer automated job search, scraping, AI matching, email reminders, attachments/CVs, recruiter messaging, calendars, salary conversion, teams, social login, and production email verification/password reset. This project is an application tracker, not a job aggregator. Real job URLs are links only; the backend must not fetch them.

## Data model

Use Django's built-in User model for this MVP; sign in with username and password. Collect username, optional email, password, and password confirmation. Do not promise email login, verified email, or unique email unless explicitly implementing those later. Passwords use Django's hashing and validators; never store them manually.

Define Application using models.Model and reference settings.AUTH_USER_MODEL:

| Field | Type / rule |
|---|---|
| id | UUID primary key, generated server-side |
| owner | ForeignKey to user, CASCADE, never writable by API client |
| company | Required trimmed string, max 120 |
| role | Required trimmed string, max 160 |
| job_url | Optional URLField, max 500; allow only http/https |
| location | Optional trimmed string, max 120, e.g. Remote LATAM |
| work_mode | choices remote / hybrid / onsite; default remote |
| status | choices saved / applied / interviewing / offer / rejected / withdrawn; default saved |
| applied_on | Nullable DateField, date-only YYYY-MM-DD |
| notes | Optional plain text, max 2000 enforced in serializer |
| created_at | DateTimeField auto_now_add |
| updated_at | DateTimeField auto_now |

Index owner/status and owner/created_at. Default ordering newest first, with a deterministic id tie-breaker. Permit duplicate company/role entries because multiple openings can share titles. Render notes as text, never unsanitized HTML.

Validation: trim required strings and reject blanks, validate choices and URLs, reject applied_on in the future relative to America/Managua, and allow null dates. A saved record has no application date. Moving saved to applied requires a date supplied by the user; later statuses may have a null date to allow historical records. Moving back to saved clears the date explicitly. On PATCH validate the resulting combined state, not just supplied fields. No enforced linear status transitions: corrections must remain possible. Reject unsupported writable fields, especially owner/id/timestamps.

## Architecture and authentication contract

Browser React → Django/DRF REST endpoint → Django ORM → database → JSON → React.

Supabase is a database host only in this project: no Supabase Auth, browser Supabase client, or direct browser database access. Django auth users are separate from Supabase auth.users. Do not copy auth.uid() RLS policies from the previous project: they do not represent Django user identities.

Use DRF's built-in token authentication as a deliberately small learning baseline for a separate-origin SPA. The header is `Authorization: Token <value>` (not Bearer). Registration does not expose password hashes. Login calls Django authenticate and creates/returns the user's token. Logout deletes the server token and clears frontend state. /auth/me verifies the current user. Default protected API permission is IsAuthenticated; explicitly mark health/register/login public. Do not enable permissive AllowAny on application routes.

Keep token only in React memory, not localStorage/sessionStorage or URLs. A full page reload requires login again; application data remains saved. This is intentional and differs from the first project's persisted session. Return a useful message on 401. DRF tokens do not expire automatically, and the standard model has one token per user; logout invalidates that token across other sessions. Document these constraints. Persistent sessions, expiring JWTs, and HttpOnly-cookie designs are later exercises, not silent substitutions.

All deployed requests containing credentials/tokens use HTTPS. Disable BasicAuthentication for the SPA API. Admin uses Django's normal session/CSRF system; do not disable CSRF globally. Add reasonable authentication throttling and explain that cache-based throttles are not a complete distributed security boundary. Never log passwords or tokens.

Ownership is enforced on the server: get_queryset filters owner=request.user for list AND detail/update/delete; perform_create assigns owner=request.user. A guessed ID belonging to another user returns 404. Counts/search/filter queries also start with this user-scoped queryset. Tests must cover these paths.

## PostgreSQL security and migration strategy

Start with SQLite for stages 1–6; switch deliberately to PostgreSQL before deployment. Django migrations create Django auth, token, admin, and application tables. Do not hand-create these tables in Supabase or use Supabase Auth migrations. SQLite data is not transferred automatically; seed fresh synthetic records in the hosted project.

Choose a dedicated Supabase project if free quota permits. Because Django connects via a database credential, disable the Supabase Data API on this dedicated project before creating Django tables. Verify public REST/GraphQL access cannot expose users, tokens, or applications. If the project is shared with another app requiring that API, do not disable it globally: stop and design a non-exposed schema with appropriate database grants instead. Avoid modifying the previous app's project.

Use the connection string copied from Supabase's Connect dialog, preferably the session pooler when IPv4 is required; do not invent host/user values. Set required SSL options, percent-encode password characters in URL credentials, and keep DATABASE_URL backend-only. Review role privileges with Codex; use only required privileges, and document if the initial learning setup uses the provider's broad database-owner credential. Do not assume RLS automatically protects direct privileged ORM connections: application ownership checks are essential.

Use a small worker count/connection budget on free tiers. Keep test databases separate: never point destructive test setup at the hosted application database. Run automated tests with local SQLite/test database, then non-destructive PostgreSQL integration checks with synthetic accounts.

## REST API contract

Use trailing slashes consistently in Django and frontend requests.

| Method | Endpoint | Behavior |
|---|---|---|
| GET | /api/health/ | Public liveness, 200 {status: ok}, no secrets |
| POST | /api/auth/register/ | username, optional email, password, password_confirm; 201 public user fields |
| POST | /api/auth/login/ | username/password; 200 {token, user}; generic 401 for bad credentials |
| GET | /api/auth/me/ | Protected, 200 public user fields |
| POST | /api/auth/logout/ | Protected, invalidate token, 204 |
| GET | /api/applications/ | Protected, paginated list; search/status filters |
| POST | /api/applications/ | Protected, create validated record, 201 record |
| GET | /api/applications/:uuid/ | Own record, 200; otherwise 404 |
| PATCH | /api/applications/:uuid/ | Partial edit, 200 record |
| DELETE | /api/applications/:uuid/ | Delete own record, 204 |
| GET | /api/applications/summary/ | Counts by status and total for current user, unfiltered |

Pagination: DRF page-number, fixed page size 20; response {count, next, previous, results}. React must implement navigation and disable unavailable pages. `?status=applied&search=python` filters company and role case-insensitively; reject unsupported status values with 400. Summary includes zero values for statuses with no records and counts the user's full dataset; label it accordingly in UI. List count reflects filters.

Use standard DRF field errors for 400 and {detail: ...} for auth/not-found errors; frontend understands both shapes. Show generic 500 messages, never stack traces. Avoid DELETE/logout response.json() on 204. Keep exact contract in README. Browser requests use fetch; no direct database client.

## Repository structure

```text
job-application-tracker/
  plan.md
  guide.md
  README.md
  .gitignore
  frontend/
    package.json
    package-lock.json
    .env.example
    src/{pages,components,lib}/
  backend/
    manage.py
    requirements.txt
    .env.example
    config/{settings,urls,wsgi}.py
    accounts/{serializers,views,urls,tests}.py
    applications/{models,serializers,views,urls,admin,tests}.py
    applications/migrations/
```

Use python -m venv and python -m pip. Do not commit .venv, .env, local SQLite files, caches, node_modules, or collected static output. Commit Django migration files. Django project config is different from a Django app such as applications.

## Environment examples

Frontend: VITE_API_BASE_URL=http://localhost:8000/api (client adds endpoint paths consistently). Production value is the actual Render HTTPS origin plus /api. No Supabase URL/key or database password in frontend.

Backend: DJANGO_SECRET_KEY placeholder; DEBUG=true locally/false online; ALLOWED_HOSTS=localhost,127.0.0.1 locally and actual Render hostname online; CORS_ALLOWED_ORIGINS=http://localhost:5173 locally and exact Vercel HTTPS origin online; DATABASE_URL only for PostgreSQL; TIME_ZONE=America/Managua; USE_TZ=True. Parse environment booleans explicitly: bool('false') is True. Parse comma-separated host/origin lists carefully. Fail startup if production secrets/configuration are absent.

CORS allows exact frontend origins and Authorization/Content-Type; this token flow does not need cross-site cookies or credentials: include. Do not configure CORS_ALLOW_ALL_ORIGINS. Vite variables are public and build-time. Keep secret/database values in backend settings only.

## Milestones / small learning sprints

### 1. Setup and first request
- [ ] Inspect existing repository/AGENTS.md; create separate workspace for this project.
- [ ] Confirm Python, Node LTS, Git and free account availability.
- [ ] Create virtual environment, Django project, DRF setup, and React frontend.
- [ ] Explain settings.py, urls.py, manage.py, project versus app.
- [ ] Implement /api/health/ and fetch it from React locally.

### 2. ORM and migrations
- [ ] Create Application model and initial migration.
- [ ] Run migrate, inspect with Django shell and optional admin locally.
- [ ] Demonstrate create/filter/update/delete using ORM with synthetic records.
- [ ] Explain makemigrations versus migrate; inspect migration files.

### 3. Django authentication
- [ ] Implement registration with Django password validation/create_user.
- [ ] Implement token login, /me, logout, protected defaults.
- [ ] Build login/register and protected frontend dashboard.
- [ ] Verify bad credentials, missing tokens, logout invalidation, reload behavior.

### 4. DRF CRUD
- [ ] Write serializer and result-state validation.
- [ ] Implement scoped list/create/detail/PATCH/delete.
- [ ] Connect frontend form/list/edit/delete with loading and error handling.
- [ ] Test two users and guessed IDs before expanding UI.

### 5. Search, filters, summary, pagination
- [ ] Implement scoped queries and status counts.
- [ ] Build frontend controls, navigation, responsive cards/table.
- [ ] Test filters together, empty pages, and summary privacy.

### 6. Verification
- [ ] Run focused Django/DRF tests for auth, ownership on every route, field/partial-update validation, filters, pagination, summary, logout.
- [ ] Run frontend production build and manual user flow.
- [ ] Seed reproducible synthetic case below; no real job scraping needed.

### 7. Hosted PostgreSQL and backend deployment
- [ ] Create/configure Supabase Free project, disable unused Data API safely.
- [ ] Configure PostgreSQL URL/SSL and run migrations against intended fresh database.
- [ ] Verify PostgreSQL integration, ownership, persistence, and public-data isolation.
- [ ] Push source without secrets to GitHub.
- [ ] Configure Render Free root backend/, pinned Python runtime, install dependencies, collectstatic with WhiteNoise if admin is used.
- [ ] Run migrate as a documented one-time controlled step. If Free lacks release/shell hooks, use the provider-supported build step for this single-instance learning deployment; do not assume paid pre-deploy hooks are available. Explain this limited migration strategy and avoid overlapping deployments.
- [ ] Start Gunicorn config.wsgi:application bound to 0.0.0.0:$PORT with a small worker budget. Windows local development uses runserver, not Gunicorn.
- [ ] Set DEBUG=false, ALLOWED_HOSTS, secrets, database URL; verify HTTPS/proxy settings against Render documentation to avoid redirect loops.
- [ ] Run python manage.py check --deploy under production settings; review findings, including admin/session HTTPS settings.
- [ ] Verify health and authenticated endpoint at real hosted URL. Do not host SQLite on Render's ephemeral filesystem.

### 8. Frontend and full deployed verification
- [ ] Deploy frontend/ on Vercel Hobby with build npm run build/output dist.
- [ ] Set VITE_API_BASE_URL to actual backend; configure safe SPA fallback for direct refresh.
- [ ] Update backend allowed CORS origin to actual frontend and redeploy.
- [ ] Verify two accounts, create/edit/status/filter/delete, data after re-login/reload.
- [ ] Test public HTTPS URL on another device/mobile data with laptop off.
- [ ] Record live URLs and redeployment/setup instructions, dependency versions, token limitations, and observed free-tier behavior.

## Synthetic acceptance case

Use fake companies/URLs, not real job offers. Account A saves:

1. Example Data Labs — Junior Data Engineer — saved — no applied_on — remote — https://example.com/jobs/data.
2. Example Backend Studio — Junior Python Developer — applied — 2026-10-01 — remote — https://example.com/jobs/python.
3. Example Analytics — Data Intern — interviewing — 2026-10-02 — hybrid — blank URL.

Account B has one separate saved record. A sees total 3 and one count in each populated status. Filtering applied returns one; searching Python returns one; A never sees B. Change first record to applied with date 2026-10-03: total stays 3, applied becomes 2, saved becomes 0. Reject whitespace company, invalid status, unsafe URL scheme, future date and applied transition without date. B cannot retrieve/PATCH/delete any A UUID; returns 404. Revoked tokens get 401. Deleting A's third record changes total to 2. All data persists after re-login and deployment restart. Adapt dates if these become future dates relative to testing day.

## Definition of done

Public hosted URL, authenticated private records, durable PostgreSQL data, meaningful tests and mobile usability. User can explain model → migration → serializer → view/queryset → URL → response, and can redeploy it. Codex reports completed versus pending checks; do not mark deployment done from build success alone.

## Official reference links (checked 2026-10-09 UTC)

- Django: https://docs.djangoproject.com/ — use selected supported version's tutorial/auth/deployment checklist.
- DRF authentication: https://www.django-rest-framework.org/api-guide/authentication/
- DRF cross-origin guidance: https://www.django-rest-framework.org/topics/ajax-csrf-cors/
- Render Django: https://render.com/docs/deploy-django
- Render Free: https://render.com/docs/free
- Supabase connection modes: https://supabase.com/docs/guides/database/connecting-to-postgres
- Supabase API hardening: https://supabase.com/docs/guides/api/securing-your-api
- Vercel Hobby: https://vercel.com/docs/plans/hobby

Recheck provider settings and quotas at implementation time; do not hardcode remembered limits.
