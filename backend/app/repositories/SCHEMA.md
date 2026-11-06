# Repository schema

Synchronous functions. `db` is a SQLAlchemy `Connection`. The caller commits. `user_id` is the integer primary key. The header `X-Dev-User` carries `external_id` (`dev-user-1`), and `get_current_user_id` turns that into `user_id`.

Lists are newest first (`created_at` descending, then `id` descending). A missing row and another user's row both come back as no row.

## users

`id`, `external_id` (unique), `name`, `created_at`. Migration inserts `dev-user-1` as id 1. The seed also inserts empty `dev-user-2`.

## notes

`id`, `user_id`, `title`, `content`, `source_type`, `source_path`, `created_at`, `updated_at`. Index `idx_notes_user` on `user_id`.

`source_path` is null for a note typed into the API. Maddie's import can send the file path. Delete removes the row.

- `list_notes(db, user_id)`
- `get_note(db, user_id, note_id)` returns `None` when the note is missing
- `create_note(db, user_id, title, content, source_type, source_path)`

## tasks

`id`, `user_id`, `title`, `due_date`, `status`, `duration_minutes`, `priority`, `created_at`, `updated_at`. Index `idx_tasks_user` on `user_id`.

`due_date` is a date. `status` is `todo` or `done`. `priority` is `low`, `medium`, `high`, or null. `duration_minutes` is a positive integer or null. Those limits live in the API, not in a database check.

- `list_active_tasks(db, user_id)` returns `status = 'todo'`
- `list_tasks(db, user_id)` returns every status. `GET /tasks` uses this, so a completed task stays visible as `done`

## interests

`id`, `user_id`, `name`, `active`, `created_at`, `updated_at`. Unique on `(user_id, name)`. Index `idx_interests_user` on `user_id`.

- `list_active_interests(db, user_id)` returns `active = true`
- `GET /interests` returns active and inactive rows so a deactivated interest can be turned back on
