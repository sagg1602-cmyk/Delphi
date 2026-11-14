# Week 2 demo — six minutes

Owner: Sebastian (#18). This is a prepared runbook, not a completed demo record.
The connected version is blocked; see [week1-week2-status.md](week1-week2-status.md).
Use [demo-student.md](demo-student.md) after fixtures/catalog are aligned.

## Preflight gate

Before inviting a live rehearsal, Manny confirms all of the following on current main:

- Core Week 2 backend routes, migration, seed and dev-user header restored.
- Maddie's note-load script and reviewed catalog merged; actual paths documented.
- `POST /recommendations/generate` registered with real sources.
- Frontend merged, correct card types, API client and Today/Tasks/Notes working.
- Browser health/CORS check succeeds; synthetic mode visibly labeled and disabled.
- Notes/resources/tasks belong to Alex; task due dates refreshed; created IDs recorded.
- A second empty user works through the shared dev-user dependency.

There is no working `python -m app.seed`, note-load command, or frontend start
command on main today. Do not copy commands from the unmerged Week 2 API branch
and describe them as runnable on main. Replace these gates with exact merged setup
commands before recording a successful connected rehearsal.

Current Week 1 backend setup is in [../backend/HANDOFF.md](../backend/HANDOFF.md):
from `backend/`, create/activate a venv, install `requirements.txt`, copy/configure
`.env`, run `python database.py`, then `uvicorn main:app --reload --port 8000`.
It requires local PostgreSQL and creates tables from schema.sql. This setup does
not provide the missing Week 2 flows. Use an isolated local database, never production.

## Connected presentation (only after preflight passes)

| Time | Action | Narration and acceptance |
| --- | --- | --- |
| 0:00–0:45 | Show local database/API, run merged seed and note-loader commands, open live `/docs` | “These are saved fictional student records.” Show task/note IDs and source fields; no fixture substitution. |
| 0:45–1:45 | In browser add primary task due in two days and a related note | “Capture work and the knowledge that can help.” Show successful writes and matching API records. |
| 1:45–2:45 | Open Today and refresh | “One study action and one discovery resource.” Confirm actual endpoint response and relevant task/catalog selection. |
| 2:45–3:45 | Open Why this? for both cards | Read task/note/interest/resource labels; resolve IDs to actual records and resource URL to catalog. Never treat a file ID as a saved ID. |
| 3:45–4:45 | Mark primary task complete, refresh Today | Its study suggestion disappears; another unfinished task may replace it. Discovery may remain. |
| 4:45–5:15 | Switch to empty dev user and refresh | Empty recommendations and “Add a task or interest to get suggestions”; no other user's data. |
| 5:15–6:00 | Read confirmed contributor statuses | Done/partial/blocked, one sentence each; name remaining owner and next step. |

## Runnable component fallback (clearly labeled, 3–5 minutes)

From repository root, Python only; no database or API keys required:

```bash
python 'backend/Maddie/Week 1/NoteReqDraft.py'
python -m backend.app.services.recommendations.demo
python -m unittest backend.app.services.recommendations.test_engine -v
```

Show ten parsed notes and three rejected malformed files (one minute). Show the
synthetic due-task, completed-task, changed-interest and empty-user scenarios
(two minutes). Show 16 passing engine tests (30 seconds). Finish by reading the
repository-audit status table and blockers (one minute). Say explicitly:
“Component behavior is verified; the browser-to-database loop is still blocked.”
This fallback does not satisfy #18's end-to-end definition of done.

## Rehearsal record (fill after running)

- Run date/time and main commit: pending.
- Setup/seed/load commands and environment: pending.
- Operator and engineer-confirmed statuses: pending.
- Created IDs, due dates and catalog version: pending.
- Six steps: each pending (record pass/fail and evidence).
- Failures, responsible owner and next action: pending.

No meeting, personal message, calendar invitation, or completed demonstration is
implied by this runbook. Keep #18 open until the required evidence exists.
