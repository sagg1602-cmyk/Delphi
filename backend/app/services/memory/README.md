# Memory Retrieval (Week 1)

Keyword search over a small list of sample notes. Issue #2.

## Run

From `backend/`:

    python -m app.services.memory.demo
    python -m unittest discover tests -v

## Function

    retrieve_notes(user_id, query, limit=5)

Returns a list, best match first, or `[]` if nothing matches:

    [
      {
        "note_id": 1,
        "title": "Photosynthesis Lecture Notes",
        "excerpt": "...membrane and make ATP. The Calvin cycle uses ATP to fix carbon dioxide into sugar.",
        "score": 0.33,
        "source_type": "markdown"
      }
    ]

Title matches count double, and `score` is between 0 and 1. Only the given user's notes are searched.

Week 2 moves this onto PostgreSQL with the same output format.
