# How to talk to the Delphi API (Week 1)

This is the agreement sheet for the first backend. It matches the code that is running now. Words: a route is the web address, JSON is the text format of the data, and snake_case means names like `due_date`.

Dev only. There is no login. Every request is the same sample user, id 1. The base address is http://localhost:8000. Docs: http://localhost:8000/docs.

A saved note looks like this:

`{"id":1,"user_id":1,"title":"Binary search trees","content":"Left < parent < right.","source_type":"manual","created_at":"2026-10-24T03:19:33.030860Z","updated_at":"2026-10-24T03:19:33.030860Z"}`

A saved task looks like this:

`{"id":1,"user_id":1,"title":"Finish problem set 4","due_date":"2026-10-30","status":"todo","created_at":"2026-10-24T03:19:33.068220Z","updated_at":"2026-10-24T03:19:33.068220Z"}`

`created_at` and `updated_at` are equal until an edit exists. Task fields are still a proposal.

| What we agree on | What it means | Example of a choice | Delphi, as built |
| --- | --- | --- | --- |
| The path (URL) | The web address of the resource | `/api/v1/users` vs `/get-all-users` | `/health`, `/notes`, `/tasks`. No `/api/v1`. Local address: http://localhost:8000. |
| The HTTP method | The action | GET fetches, POST creates, PATCH changes, DELETE removes | GET `/health`. GET and POST on `/notes` and `/tasks`. Planned for Week 2, not built: GET, PATCH, and DELETE on `/notes/{id}` and `/tasks/{id}`. |
| Request parameters | Filters in the address | `/users?status=active` vs `/users/active` | None this week. Lists return everything for the dev user, newest first. Reserved for later: `limit` and `offset` on lists, `status` on `/tasks`. |
| The request body | Data sent to the server | `firstName` vs `first_name` | Note: `title` (required), `content`, `source_type`. Task: `title` (required), `due_date`, `status`. Names use snake_case. Do not send `user_id`. |
| The response body | Data the server sends back | `{"success": true, "data": []}` vs a plain list | Creating returns the whole saved item, including `id`, `user_id`, `created_at`, and `updated_at`. Lists are plain arrays. No wrapper object. |
| Error handling | What a failure looks like | 404 vs 400 with a message | 422 means the data was invalid, and the message names the field. 503 means the database is unreachable. 404 will be used for a missing item once the by-id routes exist. No custom error format yet. |
| Authentication | How we know who is calling | a token header vs a cookie | None yet. Everyone is the same dev user (id 1), labeled dev-only. Real login comes later; the method is not decided. |

**Who needs what.** Manny: run steps and the env names `DATABASE_URL` and `TEST_DATABASE_URL` are in `backend/README.md`. Miya: the examples above, and the browser rule that allows only http://localhost:3000. Xitlaly: note columns are `id`, `user_id`, `title`, `content`, `source_type`, `created_at`, `updated_at`.

**Planned for editing in Week 2.** Get, change, and delete one note or task by id. A change sends only the fields you want to change. Sending `due_date` as null clears it.

**Open questions to confirm.** For Manny and Sebastian: (1) task fields, (2) plain responses with no wrapper, (3) snake_case names, (4) no `/api/v1` prefix. For Xitlaly and Manny: are deleted notes removed for good, or marked deleted and hidden? Retrieval has to forget them either way.
