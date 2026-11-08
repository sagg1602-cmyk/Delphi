# Memory Retrieval

PostgreSQL full-text search over the notes table. Issues #2 and #13.

## Run

From `backend/`, with Postgres running and `.env` set up (see `HANDOFF.md`):

    python -m pytest tests/test_retrieval.py -v
    python -m app.services.memory.demo
    python -m app.services.memory.recall_check

All three use `delphi_test` and roll back what they insert.

## Function (for Youssef)

    retrieve_notes(db, user_id, query, limit=5)

Returns a list, best match first, or `[]` if nothing matches:

    [
      {
        "note_id": 10,
        "user_id": 1,
        "title": "Plate Tectonics",
        "excerpt": "...or transform (slide past). Most earthquakes and volcanoes occur along plate boundaries.",
        "score": 0.196,
        "source_type": "markdown"
      }
    ]

`user_id` is included because the recommendation context filters notes by it.

To build a query from a task and interests:

    build_task_query("Draft research introduction", [{"name": "cognition", "active": True}])
    # "draft research introduction cognition"

## Route (for Miya)

    GET /notes/search?q=calvin+cycle&limit=5

Registered in `main.py` before the notes router, so a later `/notes/{id}` route won't catch `/notes/search`.

## Recall@5

10 scenarios over Maddie's 10 sample notes: **1.00**. Easy with only 10 very different notes, so it should be rerun on the 25-note set.
