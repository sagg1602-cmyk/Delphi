# Delphi backend (Week 1)

A small FastAPI app that stores notes and tasks in PostgreSQL. Dev-only foundation: there is no real login, and every request acts as one seeded user (`id` 1, name `dev-user (DEV ONLY)`).

## Prerequisites

- Python 3.11 or newer (3.13 works)
- PostgreSQL 14 or newer, or Docker

PostgreSQL is the team's database. This app does not run on anything else.

### Option A: Docker

```bash
docker run --name delphi-pg -e POSTGRES_USER=delphi -e POSTGRES_PASSWORD=delphi_dev \
  -e POSTGRES_DB=delphi -p 5432:5432 -d postgres:16
docker exec delphi-pg createdb -U delphi delphi_test
```

If the container already exists, start it with `docker start delphi-pg`.

### Option B: native install (macOS/Linux)

```bash
createuser --pwprompt delphi   # use password: delphi_dev
createdb -O delphi delphi
createdb -O delphi delphi_test
```

`delphi_dev` is a local placeholder password, not a production secret.

## Configuration

From this folder, copy the example env file:

```bash
cp .env.example .env
```

| Variable | What it does |
| --- | --- |
| `DATABASE_URL` | Connection string for the development database `delphi`. The API and `python database.py` read this. |
| `TEST_DATABASE_URL` | Connection string for `delphi_test`. Pytest reads this and refuses to run if the database name does not end in `_test`. Tests never read `DATABASE_URL`. |

Manny can copy these two names into the root `.env.example`.

## Install and run

Run every command from `backend/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python database.py
uvicorn main:app --reload --port 8000
```

`python database.py` creates the tables. It is safe to run again; it does not delete data.

Interactive docs: http://localhost:8000/docs

## Example requests

These are real responses from a local run on October 24, 2026. Timestamps are ISO 8601 in UTC.

### GET /health

```bash
curl -s -w "\nHTTP %{http_code}\n" http://localhost:8000/health
```

```text
{"status":"ok","database":"ok"}
HTTP 200
```

### POST /notes

```bash
curl -s -w "\nHTTP %{http_code}\n" -H "Content-Type: application/json" \
  -d '{"title":"Binary search trees","content":"Left < parent < right.","source_type":"manual"}' \
  http://localhost:8000/notes
```

```text
{"id":1,"user_id":1,"title":"Binary search trees","content":"Left < parent < right.","source_type":"manual","created_at":"2026-10-24T03:19:33.030860Z","updated_at":"2026-10-24T03:19:33.030860Z"}
HTTP 201
```

### GET /notes

```bash
curl -s -w "\nHTTP %{http_code}\n" http://localhost:8000/notes
```

```text
[{"id":1,"user_id":1,"title":"Binary search trees","content":"Left < parent < right.","source_type":"manual","created_at":"2026-10-24T03:19:33.030860Z","updated_at":"2026-10-24T03:19:33.030860Z"}]
HTTP 200
```

### POST /tasks

Task fields are proposed. Confirm them with Manny and Sebastian.

```bash
curl -s -w "\nHTTP %{http_code}\n" -H "Content-Type: application/json" \
  -d '{"title":"Finish problem set 4","due_date":"2026-10-30","status":"todo"}' \
  http://localhost:8000/tasks
```

```text
{"id":1,"user_id":1,"title":"Finish problem set 4","due_date":"2026-10-30","status":"todo","created_at":"2026-10-24T03:19:33.068220Z","updated_at":"2026-10-24T03:19:33.068220Z"}
HTTP 201
```

### GET /tasks

```bash
curl -s -w "\nHTTP %{http_code}\n" http://localhost:8000/tasks
```

```text
[{"id":1,"user_id":1,"title":"Finish problem set 4","due_date":"2026-10-30","status":"todo","created_at":"2026-10-24T03:19:33.068220Z","updated_at":"2026-10-24T03:19:33.068220Z"}]
HTTP 200
```

### Invalid input (422)

A title that is empty after trimming is rejected. The message names the field. Do not send `user_id`; that is also a 422.

```bash
curl -s -w "\nHTTP %{http_code}\n" -H "Content-Type: application/json" \
  -d '{"title":"   "}' http://localhost:8000/notes
```

```text
{"detail":[{"type":"string_too_short","loc":["body","title"],"msg":"String should have at least 1 character","input":"","ctx":{"min_length":1}}]}
HTTP 422
```

## Run the test

From `backend/`, with the virtualenv active and `delphi_test` created:

```bash
pytest
```

A pass looks like this:

```text
test_main.py::test_notes_and_tasks_persist_across_restart PASSED
test_main.py::test_empty_title_is_rejected PASSED
test_main.py::test_health_ok PASSED
3 passed, 1 warning in 0.35s
```

The warning says Starlette would prefer the `httpx2` package. The tests use `httpx`, and they still pass. Pytest never connects to the `delphi` database.

## Demo script (about 2 minutes)

1. Start PostgreSQL (`docker start delphi-pg` if you used Option A).
2. From `backend/`, activate `.venv` and run `uvicorn main:app --reload --port 8000`.
3. Open http://localhost:8000/docs and show the five routes: GET `/health`, GET and POST `/notes`, GET and POST `/tasks`.
4. `curl http://localhost:8000/health` and show `{"status":"ok","database":"ok"}`.
5. Create a note and a task with the POST curls above. Then GET `/notes` and GET `/tasks`.
6. Stop the server with Ctrl+C. Start it again with the same uvicorn command.
7. GET `/notes` and GET `/tasks` again. The same ids and titles are still there. `created_at` and `updated_at` match, because nothing has been edited.

## Schema summary

`users` (dev seed only): `id`, `name`, `created_at`. Row 1 is `dev-user (DEV ONLY)`.

`notes`: `id`, `user_id`, `title`, `content`, `source_type`, `created_at`, `updated_at`. Index `idx_notes_user` on `user_id`.

`tasks`: `id`, `user_id`, `title`, `due_date`, `status`, `created_at`, `updated_at`. Index `idx_tasks_user` on `user_id`.

`status` may be `todo` or `done`. That list lives in `TaskStatus` in `models.py`. There is no database CHECK, so adding a status later is a code change. On insert, `updated_at` equals `created_at`. Lists come back newest first (`created_at` descending, then `id` descending), as plain arrays, for the dev user only.

## Assumptions, limitations, and Week 2+

Assumptions:

- Manny's repo has empty `backend/app/` folders and no agreed JSON fixture, so route and field names follow the Week 1 contract. His `.gitkeep` files were not changed. The runnable modules stay flat in `backend/` so this work does not edit his layout.
- Task fields (`title`, `due_date`, `status`) are a proposal.
- Clients never send `user_id`. The dependency `get_current_user_id()` supplies `1` and is marked dev-only.
- CORS allows only `http://localhost:3000`. The allowed methods include GET, POST, PATCH, and DELETE so a later edit route does not need a CORS change. PATCH and DELETE routes are not implemented.
- A total count, if we ever need one, belongs in a response header. List bodies stay arrays. Reserved query names for later, not accepted now: `limit` and `offset` on both lists, and `status` on `/tasks`.

Not built this week: login, edit and delete, get-by-id, search, recommendations, Alembic, an ORM, an async database layer, Docker Compose, and CI.

Week 2+ (designed, not built):

- `GET`, `PATCH`, and `DELETE` on `/notes/{id}` and `/tasks/{id}`.
- PATCH sends only the fields that change. At least one field is required. `due_date: null` clears a task due date. `title` and `status` cannot be null. `id`, `user_id`, and `created_at` cannot be edited. Every update must set `updated_at = now()` in the SQL. There is no database trigger.
- Missing items return 404 `{"detail": "Note not found"}` (same idea for tasks). A missing row and a row owned by someone else should look the same.
- Hard delete versus soft delete is open, because Xitlaly's retrieval has to forget deleted notes.
- Real authentication in place of the dev user, then migrations, then wiring to retrieval and the Next.js app.
