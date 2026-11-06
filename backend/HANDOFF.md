# Delphi API (dev only)

One place for the contract and how to run it. There is no login. Send `X-Dev-User: dev-user-1`, or send no header and the API uses `dev-user-1`. JSON `user_id` stays an integer. `dev-user-1` is user id `1`.

The live docs are at http://localhost:8000/docs while the server is running. `swagger.html` in this folder is the saved Week 1 page, so it does not list the new routes.

A route is the web address. JSON is the text format of the data. snake_case means names like `due_date`.

## What we agree on

A saved note:

`{"id":1,"user_id":1,"title":"Binary search trees","content":"Left < parent < right.","source_type":"manual","source_path":"notes/binary-search.md","created_at":"2026-11-06T08:00:00.000000Z","updated_at":"2026-11-06T08:00:00.000000Z"}`

A saved task:

`{"id":1,"user_id":1,"title":"Finish problem set 4","due_date":"2026-10-30","status":"todo","duration_minutes":90,"priority":"high","created_at":"2026-11-06T08:00:00.000000Z","updated_at":"2026-11-06T08:00:00.000000Z"}`

A saved interest:

`{"id":1,"user_id":1,"name":"python","active":true,"created_at":"2026-11-06T08:00:00.000000Z","updated_at":"2026-11-06T08:00:00.000000Z"}`

`created_at` and `updated_at` are equal until an edit. Timestamps are ISO 8601 in UTC. The date field on a task is `due_date`. Marking a task completed sends `"status": "done"`.

| What we agree on | What it means | Delphi, as built |
| --- | --- | --- |
| The path (URL) | The web address of the resource | `/health`, `/notes`, `/notes/{id}`, `/tasks`, `/tasks/{id}`, `/interests`, `/interests/{id}`. No `/api/v1`. Local address: http://localhost:8000. |
| The HTTP method | The action | GET fetches, POST creates, PATCH changes, DELETE removes. |
| The request body | Data sent to the server | Names use snake_case. Do not send `id` or `user_id`. A PATCH sends only the fields to change. |
| The response body | Data the server sends back | Creating and updating return the whole saved item. Lists are plain arrays, newest first. No wrapper object. |
| Error handling | What a failure looks like | 422 means the data was invalid. 404 `{"detail": "Note not found"}` is a missing note or someone else's note. Tasks and interests use the same shape. An unknown `X-Dev-User` is 404 `{"detail": "User not found"}`. A repeated interest name for the same user is 409. 503 means the database is unreachable. |
| Authentication | How we know who is calling | Header `X-Dev-User`. Missing header means `dev-user-1`. `get_current_user_id` in `app/api/deps.py` is the only place Week 3 replaces. |

**Who needs what.** Xitlaly and Youssef: import from `app.repositories` while the working directory is `backend/`. The function list and columns are in [app/repositories/SCHEMA.md](app/repositories/SCHEMA.md). Youssef's active rows are `list_active_tasks` (`status` is `todo`) and `list_active_interests` (`active` is true). `GET /tasks` still returns done tasks. Miya: the examples below, and the browser rule that allows only http://localhost:3000. `allow_headers` is `*`, so the browser may send `X-Dev-User`. Maddie: `POST /notes` accepts `title`, `content`, `source_type`, and `source_path`. Do not send the file's line-2 id. The server assigns `id`. `source_path` is the file path, and it can be omitted.

## Repository functions

Plain synchronous functions. `db` is an open SQLAlchemy connection. The caller commits.

```python
list_active_tasks(db, user_id)
list_active_interests(db, user_id)
list_notes(db, user_id)
get_note(db, user_id, note_id)
create_note(db, user_id, title, content, source_type, source_path)
```

`get_note` returns `None` when the id is missing or belongs to another user.

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

If this database was created by Week 1's `schema.sql`, drop those tables before the first migration. Alembic will not alter them in place.

```bash
psql "postgresql://delphi:delphi_dev@localhost:5432/delphi" -c \
  "DROP TABLE IF EXISTS interests, tasks, notes, users CASCADE"
```

Repeat that for `delphi_test` if a migration fails because the tables already exist. Pytest rebuilds `delphi_test` itself.

## Configuration

From `backend/`:

```bash
cp .env.example .env
```

| Variable | What it does |
| --- | --- |
| `DATABASE_URL` | Connection string for the development database `delphi`. Alembic, the API, and `python -m app.seed` read this. |
| `TEST_DATABASE_URL` | Connection string for `delphi_test`. Pytest reads this and refuses to run if the database name does not end in `_test`. Tests never read `DATABASE_URL`. |

## Install and run

Run every command from `backend/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn main:app --reload --port 8000
```

`alembic upgrade head` creates the tables. It does not delete data. `python database.py` runs that same upgrade. The API does not migrate on startup. `python -m app.seed` ensures `dev-user-1` and empty `dev-user-2`, then inserts sample tasks and interests if those titles and names are not already there. It does not insert notes. Then open http://localhost:8000/docs.

The only migration in this change is `0001_initial` in `backend/alembic/versions/`. One migration per pull request, and only Ava edits that directory.

## Example requests

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
  -d '{"title":"Binary search trees","content":"Left < parent < right.","source_type":"manual","source_path":"notes/binary-search.md"}' \
  http://localhost:8000/notes
```

```text
{"id":1,"user_id":1,"title":"Binary search trees","content":"Left < parent < right.","source_type":"manual","source_path":"notes/binary-search.md","created_at":"2026-11-06T08:00:00.000000Z","updated_at":"2026-11-06T08:00:00.000000Z"}
HTTP 201
```

Omit `source_path` and the saved value is null. Omit `source_type` and it is `manual`.

### GET /notes

```bash
curl -s -w "\nHTTP %{http_code}\n" http://localhost:8000/notes
```

```text
[{"id":1,"user_id":1,"title":"Binary search trees","content":"Left < parent < right.","source_type":"manual","source_path":"notes/binary-search.md","created_at":"2026-11-06T08:00:00.000000Z","updated_at":"2026-11-06T08:00:00.000000Z"}]
HTTP 200
```

### GET /notes/{id}

```bash
curl -s -w "\nHTTP %{http_code}\n" http://localhost:8000/notes/1
```

```text
{"id":1,"user_id":1,"title":"Binary search trees","content":"Left < parent < right.","source_type":"manual","source_path":"notes/binary-search.md","created_at":"2026-11-06T08:00:00.000000Z","updated_at":"2026-11-06T08:00:00.000000Z"}
HTTP 200
```

A missing id, or another user's id, is `{"detail":"Note not found"}` with HTTP 404.

### DELETE /notes/{id}

```bash
curl -s -w "\nHTTP %{http_code}\n" -X DELETE http://localhost:8000/notes/1
```

```text

HTTP 204
```

The body is empty. The row is removed. A missing id is HTTP 404 `{"detail":"Note not found"}`.

### POST /tasks

```bash
curl -s -w "\nHTTP %{http_code}\n" -H "Content-Type: application/json" \
  -d '{"title":"Finish problem set 4","due_date":"2026-10-30","status":"todo","duration_minutes":90,"priority":"high"}' \
  http://localhost:8000/tasks
```

```text
{"id":1,"user_id":1,"title":"Finish problem set 4","due_date":"2026-10-30","status":"todo","duration_minutes":90,"priority":"high","created_at":"2026-11-06T08:00:00.000000Z","updated_at":"2026-11-06T08:00:00.000000Z"}
HTTP 201
```

`duration_minutes` and `priority` can be omitted. They are stored as null. `priority` is `low`, `medium`, or `high`.

### GET /tasks

```bash
curl -s -w "\nHTTP %{http_code}\n" http://localhost:8000/tasks
```

```text
[{"id":1,"user_id":1,"title":"Finish problem set 4","due_date":"2026-10-30","status":"todo","duration_minutes":90,"priority":"high","created_at":"2026-11-06T08:00:00.000000Z","updated_at":"2026-11-06T08:00:00.000000Z"}]
HTTP 200
```

This list includes `done` tasks. `list_active_tasks` is the repository function that returns only `todo`.

### PATCH /tasks/{id}

```bash
curl -s -w "\nHTTP %{http_code}\n" -X PATCH -H "Content-Type: application/json" \
  -d '{"status":"done"}' \
  http://localhost:8000/tasks/1
```

```text
{"id":1,"user_id":1,"title":"Finish problem set 4","due_date":"2026-10-30","status":"done","duration_minutes":90,"priority":"high","created_at":"2026-11-06T08:00:00.000000Z","updated_at":"2026-11-06T08:05:00.000000Z"}
HTTP 200
```

Send only the fields to change: `title`, `status`, `due_date`, `duration_minutes`, `priority`. `"due_date": null` clears the date. The same null clears `duration_minutes` and `priority`. `title` and `status` cannot be null. `updated_at` changes. A missing task is HTTP 404 `{"detail":"Task not found"}`.

### POST /interests

```bash
curl -s -w "\nHTTP %{http_code}\n" -H "Content-Type: application/json" \
  -d '{"name":"python"}' \
  http://localhost:8000/interests
```

```text
{"id":1,"user_id":1,"name":"python","active":true,"created_at":"2026-11-06T08:00:00.000000Z","updated_at":"2026-11-06T08:00:00.000000Z"}
HTTP 201
```

The same user and the same name again is HTTP 409 `{"detail":"Interest already exists"}`.

### GET /interests

```bash
curl -s -w "\nHTTP %{http_code}\n" http://localhost:8000/interests
```

```text
[{"id":1,"user_id":1,"name":"python","active":true,"created_at":"2026-11-06T08:00:00.000000Z","updated_at":"2026-11-06T08:00:00.000000Z"}]
HTTP 200
```

Inactive interests stay in this list. `list_active_interests` is the repository function that returns only `active` rows.

### PATCH /interests/{id}

```bash
curl -s -w "\nHTTP %{http_code}\n" -X PATCH -H "Content-Type: application/json" \
  -d '{"active":false}' \
  http://localhost:8000/interests/1
```

```text
{"id":1,"user_id":1,"name":"python","active":false,"created_at":"2026-11-06T08:00:00.000000Z","updated_at":"2026-11-06T08:05:00.000000Z"}
HTTP 200
```

Send `active` true to turn it back on. A missing interest is HTTP 404 `{"detail":"Interest not found"}`.

### Invalid input (422)

A title that is empty after trimming is rejected. The message names the field. Sending `user_id` or `id` is also a 422.

```bash
curl -s -w "\nHTTP %{http_code}\n" -H "Content-Type: application/json" \
  -d '{"title":"   "}' http://localhost:8000/notes
```

```text
{"detail":[{"type":"string_too_short","loc":["body","title"],"msg":"String should have at least 1 character","input":"","ctx":{"min_length":1}}]}
HTTP 422
```

### Second user

`python -m app.seed` creates `dev-user-2` with no rows. The same calls with the header return empty lists.

```bash
curl -s -w "\nHTTP %{http_code}\n" -H "X-Dev-User: dev-user-2" http://localhost:8000/notes
```

```text
[]
HTTP 200
```

`GET /tasks` and `GET /interests` with that header are `[]` as well. `GET /notes/1` with that header is HTTP 404.

## Run the test

From `backend/`, with the virtualenv active and `delphi_test` created:

```bash
pytest
```

Pytest rebuilds `delphi_test` from the migration, then checks persistence, deletion, the second user, and health. It also runs the recommendation tests under `app/services/recommendations/`. Pytest never connects to the `delphi` database.

A pass looks like this:

```text
24 passed, 1 warning, 8 subtests passed
```

The warning says Starlette would prefer the `httpx2` package. The tests use `httpx`, and they still pass.

## Demo script (about 3 minutes)

The seed already inserts tasks and interests, so the new task is not id 1. Use the ids printed by the create commands.

1. Start PostgreSQL (`docker start delphi-pg` if you used Option A).
2. From `backend/`, activate `.venv`. Run `alembic upgrade head`, then `python -m app.seed`, then `uvicorn main:app --reload --port 8000`.
3. In a second terminal, from `backend/`, create one note, one task, and one interest:

```bash
NOTE=$(curl -s -H "Content-Type: application/json" \
  -d '{"title":"Binary search trees","content":"Left < parent < right.","source_type":"manual","source_path":"notes/binary-search.md"}' \
  http://localhost:8000/notes)
TASK=$(curl -s -H "Content-Type: application/json" \
  -d '{"title":"Demo task","due_date":"2026-10-30","status":"todo"}' \
  http://localhost:8000/tasks)
INTEREST=$(curl -s -H "Content-Type: application/json" \
  -d '{"name":"astronomy"}' \
  http://localhost:8000/interests)
printf '%s\n' "$NOTE" "$TASK" "$INTEREST"
NOTE_ID=$(printf '%s' "$NOTE" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
TASK_ID=$(printf '%s' "$TASK" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")
```

4. Mark that task completed and delete that note:

```bash
curl -s -H "Content-Type: application/json" -X PATCH \
  -d '{"status":"done"}' "http://localhost:8000/tasks/$TASK_ID"
echo
curl -s -o /dev/null -w "DELETE HTTP %{http_code}\n" -X DELETE \
  "http://localhost:8000/notes/$NOTE_ID"
```

The patch response has `"status":"done"` and a later `updated_at`. Delete prints `DELETE HTTP 204`.

5. Stop the server with Ctrl+C. Start it again with the same uvicorn command.
6. Show that the lists survived the restart:

```bash
curl -s "http://localhost:8000/notes/$NOTE_ID"
echo
curl -s http://localhost:8000/notes
echo
curl -s http://localhost:8000/tasks
echo
curl -s http://localhost:8000/interests
echo
```

The note request is `{"detail":"Note not found"}`. `GET /notes` no longer includes that note. `GET /tasks` still includes `Demo task` with `"status":"done"`, plus the seeded tasks. `GET /interests` still includes `astronomy`, plus `python` and `sql` from the seed.

7. Show that the second user sees none of it:

```bash
curl -s -H "X-Dev-User: dev-user-2" http://localhost:8000/notes; echo
curl -s -H "X-Dev-User: dev-user-2" http://localhost:8000/tasks; echo
curl -s -H "X-Dev-User: dev-user-2" http://localhost:8000/interests; echo
```

Each body is `[]`.

## Schema

`users`: `id`, `external_id`, `name`, `created_at`. `external_id` is unique. The migration inserts `dev-user-1`. The seed inserts `dev-user-2` with no tasks, notes, or interests.

`notes`: `id`, `user_id`, `title`, `content`, `source_type`, `source_path`, `created_at`, `updated_at`. Index `idx_notes_user` on `user_id`. `source_path` is null when the client omits it.

`tasks`: `id`, `user_id`, `title`, `due_date`, `status`, `duration_minutes`, `priority`, `created_at`, `updated_at`. Index `idx_tasks_user` on `user_id`.

`interests`: `id`, `user_id`, `name`, `active`, `created_at`, `updated_at`. Unique on `(user_id, name)`. Index `idx_interests_user` on `user_id`.

`status` may be `todo` or `done`. That list lives in `TaskStatus` in `app/schemas/tasks.py`. `priority` may be `low`, `medium`, or `high`. There is no database CHECK, so adding a value later is a code change. On insert, `updated_at` equals `created_at`. Every update sets `updated_at = now()` in the SQL. There is no database trigger. Lists come back newest first (`created_at` descending, then `id` descending), as plain arrays, for the caller only.

## Where the code lives

- Routes: `backend/app/api/`
- The dev-user dependency: `backend/app/api/deps.py`
- Queries: `backend/app/repositories/`
- Request and response models: `backend/app/schemas/`
- Engine and Alembic helper: `backend/app/core/database.py`
- Seed: `backend/app/seed.py`
- `backend/main.py` and `backend/database.py` are the run commands and call those modules

CORS allows only `http://localhost:3000`. Allowed methods include GET, POST, PATCH, and DELETE.

Not built: login, search, recommendations stored in the database, notification tables, an `/api/v1` prefix, and custom error bodies beyond the status codes above.
