# Hands-on Guide — Job Application Tracker with Django

## Instructions to Codex

Read plan.md for requirements and this guide for teaching behavior. This is a new project after the completed task tracker. Do not modify the previous application. My goal is to practice Python/backend/SQL; keep React work modest. You may scaffold or implement UI when I ask, but leave key Django code to me.

Work one stage at a time. At every stage: explain the purpose, give one small task with commands/file paths, state expected output, review my result, and ask a short understanding question. Wait before advancing; do not silently complete later stages. Give skeletons/pseudocode and progressively stronger hints before full solutions. Take over a step only when I ask. Fix errors with me instead of replacing everything.

Adapt commands to my actual terminal, normally Windows PowerShell. Distinguish commands run in project root, backend/, frontend/, Django shell, or provider dashboards. Explain commands before I run them. Never ask me to paste passwords/tokens/DATABASE_URL or unredacted .env contents. Keep credentials local or in dashboards. When terminal output is needed, tell me what to redact.

Use only Vercel Hobby, Supabase Free, and Render Free. Confirm current quotas across existing projects; do not delete previous resources or buy upgrades. Account sign-in, MFA/CAPTCHA, email confirmations, resource selection, and first deployment settings are my actions. Codex reviews and diagnoses; authorized automation may be used later when I request it.

## Responsibilities

| I practice | Codex supports |
|---|---|
| Python environment, Django commands | Explain each command and confirm working directory |
| Model fields and relations | Give a model skeleton and review design |
| Migrations and ORM queries | Explain generated SQL/schema effects |
| Serializer validation | Give test cases and debug partial updates |
| Views, ownership, auth endpoints | Review correctness and security boundaries |
| API testing and two-user checks | Guide test requests; keep tokens private |
| Hosted DB and first deployment | Current dashboard instructions/log diagnosis |
| Explaining request flow | Correct misunderstandings using my own code |

Frontend layout, repetitive configuration, and test boilerplate can be delegated so I focus on Python. Do not delegate to subagents unless I explicitly request it.

## Stage 0 — What changes from Express?

Read plan.md and explain this mapping with me:

| Previous project | This project |
|---|---|
| Node runtime | Python interpreter |
| Express app/routes | Django project URLconf + DRF views |
| Manual request-body checks | DRF serializers and validators |
| Database client requests | Django ORM queries |
| SQL migration setup | Django model migration files |
| Supabase Auth identities | Django User/password hashing + DRF tokens |
| React/Vite browser UI | React/Vite remains the UI |

My task: explain where React, Django, PostgreSQL, and Supabase run. Understand that Django is the framework, DRF adds API tooling, and Supabase is only the PostgreSQL host. Explain why this is still a REST API.

Checkpoint: which responsibilities does Django provide that we previously assembled in Express?

## Stage 1 — Environment and health endpoint

1. Create job-application-tracker/ and place plan.md/guide.md in its root.
2. Check Python, Node/npm and Git versions. Ask Codex to confirm supported Python/Django/DRF compatibility.
3. Create backend/ and a virtual environment. PowerShell example inside backend/: `py -m venv .venv`, then `.\.venv\Scripts\Activate.ps1`. If activation is restricted, use `.\.venv\Scripts\python.exe` directly; do not change machine-wide security settings unnecessarily.
4. Use the selected interpreter with `python -m pip` to install the chosen supported packages. Save a reproducible requirements.txt with reviewed resolved versions. Avoid mixing global Python and virtual-environment pip.
5. Inside backend/, run `python -m django startproject config .`. Inspect manage.py, settings.py, urls.py and wsgi.py.
6. Configure DRF and write /api/health/ with Codex's minimal skeleton. Run `python manage.py runserver` and open http://127.0.0.1:8000/api/health/.
7. Scaffold React/Vite in frontend/ with the current supported command. Fetch health from React. Configure exact-origin CORS and inspect the browser Network panel.

Expected: a real browser request reaches Django and returns JSON. Django runserver is development-only; production will use Gunicorn.

Checkpoint: what does urls.py do before a view executes?

## Stage 2 — Model and migration

1. Run `python manage.py startapp applications`, register it, and inspect generated files.
2. Write Application fields from plan.md. Use settings.AUTH_USER_MODEL for the owner; do not create a second user identity system.
3. Run `python manage.py makemigrations applications`. Open the generated migration; identify operations.
4. Run `python manage.py migrate` on local SQLite. Observe that Django creates its built-in auth/admin tables too.
5. Use `python manage.py shell` to create a synthetic user with create_user, create an application, filter it, change status and delete a synthetic row. Exit the shell before terminal commands.
6. Register the model in Django admin if useful. Create a local superuser privately and inspect /admin/. Do not expose a seeded/default admin password in source.

Codex: explain ForeignKey/CASCADE, choices, UUID defaults, QuerySet laziness and why model choices alone do not replace API validation. Help distinguish shell experiments from tests.

Expected: schema and records exist locally; migrations are committed, db.sqlite3 is not.

Checkpoint: what is the difference between makemigrations and migrate? What would happen if we changed a field but ran neither?

## Stage 3 — Authentication in Django

1. Create accounts app and registration serializer. I write username/password/password-confirm checks, invoke Django password validators and use create_user.
2. Implement generic login with authenticate and DRF token creation. Configure rest_framework.authtoken and run its migrations.
3. Configure TokenAuthentication and IsAuthenticated by default; health/register/login are explicitly public.
4. Implement /me and logout, deleting the server token.
5. Test register/login/me/logout with a local request tool. Send `Authorization: Token ...`, not Bearer. Never put tokens in URLs/logs/chat.
6. Connect React login/register with an in-memory token and protected dashboard. Reloading requires login again; do not silently persist the token to browser storage.

Codex: explain authentication versus authorization, password hashes, token limits and logout across sessions. Keep Django admin session/CSRF protection intact. Explain why this separate-origin API uses token headers instead of cross-site session cookies.

Expected: missing/invalid/revoked token gets 401; bad login reveals no account details.

Checkpoint: why is Supabase Auth not involved here, and why does a reload clear login but not database records?

## Stage 4 — Serializer and first complete CRUD flow

1. Write ApplicationSerializer. Mark server-controlled fields read-only and reject attempts to supply ownership.
2. Write trimmed string, URL scheme, status and date validation. On PATCH merge existing values with incoming values when checking resulting state.
3. Implement list/create first. Scope queryset to request.user; assign owner in perform_create.
4. Connect the add form and list to these routes. Follow trailing-slash and response conventions in plan.md.
5. Implement retrieve/PATCH/delete through the same scoped queryset. Test status/date transition and ordinary company/notes edits.
6. Handle API field errors, unauthorized responses and empty 204 bodies on the frontend.

Codex: provide a skeleton of generic views/viewsets; explain each override. Help choose one clear DRF approach and use it consistently. Do not hide ownership logic behind unexplained code.

Expected: create → list → edit → delete works; other-user UUIDs return 404.

Checkpoint: what is the serializer's job, and why do permission classes alone not filter records by owner?

## Stage 5 — Queries worth practicing

1. Add status filtering; reject unknown filter values.
2. Use ORM Q objects to search company OR role without breaking owner scoping.
3. Add page-number pagination, fixed size 20, and React previous/next controls.
4. Compute summary counts by status using ORM aggregation. Explain the difference between list count (filtered) and summary total (unfiltered owned records).
5. Test search+status together, zero results, page boundaries and stable ordering.

Codex: let me write query logic; compare the ORM expression with its conceptual SQL. Do not fetch every user's records and filter them in JavaScript.

Checkpoint: where does filtering occur, and why does owner scoping have to apply before aggregation?

## Stage 6 — Test before hosting

1. Create API tests using Django/DRF testing tools with local test DB only.
2. Test two users across list/detail/create/PATCH/delete/summary/search. Confirm ownership cannot be changed through a body.
3. Test password validation, generic login failure, token invalidation and unauthorized endpoints.
4. Test required strings, URL schemes, choices, date rules and partial-update combined state.
5. Execute synthetic acceptance case in plan.md and run frontend production build.
6. Explain a failed test, fix its cause, then rerun relevant checks.

Codex: help with fixture/test boilerplate after I write the central assertions. Never run destructive tests against the live database. Do not claim SQLite tests prove every PostgreSQL behavior.

Expected: `python manage.py test` and frontend build pass; meaningful two-user checks pass.

## Stage 7 — Switch to hosted PostgreSQL deliberately

1. Inspect Supabase Free project availability; leave the previous tracker untouched. Create a dedicated project if quota permits.
2. Before Django migrations, disable the dedicated project's unused Data API and confirm it does not serve another app. If shared, stop and plan a non-exposed schema instead.
3. Copy the correct database connection URL from Connect; use session pooler when IPv4 is needed and SSL as documented. Keep password private; URL-encode special characters.
4. Set DATABASE_URL only in backend .env, configure dj-database-url/psycopg, and explain switching from SQLite.
5. Confirm the intended database target without printing credentials. Run migrate against the fresh project.
6. Create synthetic users/records and verify ORM writes/reads and account isolation. Confirm Django user/token/application tables are not accessible through public Supabase APIs.

Codex: help budget connections and privileges, explain why auth.uid() policies from our former Supabase Auth app do not match these users. Django manages passwords and migrations now. Do not transfer old application data automatically.

Checkpoint: what is Django doing that Supabase's database dashboard does not do for us?

## Stage 8 — Backend online

1. Create GitHub repository, review .gitignore and staged files, commit and push without .env/db.sqlite3/.venv.
2. Configure production settings: DEBUG false parsed correctly, exact ALLOWED_HOSTS, secret key, database URL, CORS and trusted HTTPS proxy handling.
3. On Render select a Free Python web service, root backend/, compatible pinned Python version, dependency build command and /api/health/ health path.
4. Configure Gunicorn to run config.wsgi:application on 0.0.0.0:$PORT. Keep worker count small.
5. If using admin, configure WhiteNoise/static settings and collectstatic. Do not add file uploads; free filesystem is not durable.
6. Arrange migrate through a supported free deployment workflow. If no free shell/release hook exists, review a controlled migration build step for this single-instance project; do not assume paid hooks are free.
7. Enter backend environment values privately, deploy, inspect logs and open health URL. Check --deploy findings under production settings and resolve relevant ones.

Codex: use current official Render/Django instructions, explain build versus start and migration timing. Do not assume a successful build proves API/database availability.

Checkpoint: why would SQLite data disappear on a hosting restart while hosted PostgreSQL data remains?

## Stage 9 — Frontend online and demonstration

1. Import repository to Vercel Hobby, root frontend/, Vite build npm run build and output dist.
2. Set public VITE_API_BASE_URL to actual backend HTTPS URL plus /api; rebuild after changes.
3. Add a safe SPA fallback for /login, /register and /applications direct navigation; preserve assets.
4. Set exact Vercel origin in Django CORS and redeploy backend. No database/password/token in Vite variables.
5. Register two synthetic accounts at deployed app. Create, edit, change status, filter, and delete records; verify isolation.
6. Reload, log in again, and verify saved records. Log out and confirm token no longer works.
7. Open URL on another device/mobile data with laptop off. Test layout and direct route refresh.
8. Write README with actual URLs, setup steps, token/reload behavior, deployment commands, migration procedure and observed free-tier limits.

Codex: review each result and update plan.md checkboxes. Report unresolved blockers honestly. Avoid over-polishing frontend before deployment works.

## Finish-line explanation I should be able to give

When I submit an application, React sends JSON with a token to Django. Django authenticates the user, DRF validates input, the view assigns ownership, the ORM writes to PostgreSQL, and JSON comes back. Another user's queryset cannot retrieve my records. Vercel serves the built frontend, Render runs Python, and Supabase stores the database. Django migrations make the schema reproducible.

## Starter prompt

> Read plan.md and guide.md, then inspect the repository instructions. This is a new job application tracker using React/Vite and Django/DRF; leave my completed task tracker untouched. Teach me one stage at a time. I want to write the key Python models, serializers, authentication, views and ORM queries myself. Give small tasks, skeletons, expected results and reviews, then wait before advancing. You can help with frontend and boilerplate when I request it. Use only Vercel Hobby, Supabase Free PostgreSQL and Render Free. Start with stage 0 and check my environment before giving installation commands.
