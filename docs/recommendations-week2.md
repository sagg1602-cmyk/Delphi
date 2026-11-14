# Week 2 Recommendations — Issue #15

## Current status

Implemented and tested with synthetic data:
- Deterministic recommendation engine.
- Context builder with replaceable data sources.
- Response schema and standalone API router.
- Input/output fixtures for frontend development.
- 16 engine tests, 2 API tests, and an eight-scenario demo.

Real-data integration is pending. The router is not yet registered
in the main application. This does not yet complete Issue #15.

## Setup

From the repository root:

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
python -m pip install -r backend/requirements.txt
```

No database is required for the tests and demo below.

## Run tests and demo

From the repository root:

```bash
python -m unittest backend.app.services.recommendations.test_engine -v
(cd backend && python -m unittest test_recommendations_api -v)
python -m backend.app.services.recommendations.demo
```

The API tests register the router in a temporary FastAPI application
and explicitly override the context dependency with fake data.
They do not test PostgreSQL or real data-source integration.

## Frontend contract

POST /recommendations/generate returns:

```json
{"recommendations": []}
```

Each recommendation contains:
- id: recommendation identifier
- type: study or discovery
- title: card heading
- reason: explanation based on input data
- estimated_minutes: suggested session length, not a completion prediction
- evidence: items with type, id, and human-readable label
- action: proposed object with type and target

Proposed actions:
- open_task: target is the task ID
- open_url: target is the catalog resource URL

Confirm the action structure with Miya before live wiring.

Fixtures:
- shared/fixtures/recommendations_week2.input.json
- shared/fixtures/recommendations_week2.output.json

IDs may be integers or strings. Evidence IDs preserve input ID types.
Recommendation IDs are deterministic identifiers, not saved database rows.

## Selection rules

Return at most one study recommendation and one discovery recommendation.

Study:
- Only the requested user's todo or in_progress tasks are eligible.
- Completed and cancelled tasks are excluded.
- Earlier deadlines rank first; undated tasks follow dated tasks.
- A relevant note breaks equal-deadline ties.
- Task ID breaks remaining ties.

Discovery:
- Only active interests belonging to the requested user are eligible.
- Resource tags must match an active interest name after trimming
  whitespace and ignoring case.
- Rank by the number of distinct matching interests, then note
  keyword overlap, then resource ID.

Notes currently use simple keyword overlap. Integration with the
retrieval team's query helper and retrieve_notes is pending.

No usable candidates means an empty list. Notes alone do not create
a recommendation. No model calls are made, and no recommendations
are saved.

## Evidence

Every evidence item refers to a record supplied in the input context.
The engine validates evidence IDs and checks that a discovery URL
belongs to its cited catalog resource.

Tests verify input membership and reject invented evidence and URLs.

## Context builder and data sources

build_user_context(db, user_id, *, sources, today=None) gathers and
filters data. The sources adapter exposes:

- list_tasks(db, user_id)
- list_interests(db, user_id)
- retrieve_notes(db, user_id, tasks, interests)
- load_catalog()

These are internal adapter interfaces. They must be connected to
the teammates' actual function signatures and data formats.

Normalized interests contain id, user_id, name, and active.
Normalized resources contain id, title, tags, and url.

FakeSources reads the synthetic input fixture and is only for
explicit tests and demos. It is not an automatic production fallback.

## Router integration handoff

Router module: app.api.recommendations

In backend/main.py, import:

```python
from app.api.recommendations import router as recommendations_router
```

Inside create_app(), after creating app, register:

```python
app.include_router(recommendations_router)
```

The router uses database.get_current_user_id and app.state.engine.
A real sources adapter must be assigned to
app.state.recommendation_sources before requests can generate results.
Without a configured adapter, the registered route returns HTTP 503.

## Pending work

- Connect Ava's task and active-interest repository functions.
- Connect Xitlaly's query helper and PostgreSQL retrieve_notes.
- Load Maddie's resources.json.
- Confirm data formats and the frontend action structure.
- Register the router and configure the real sources adapter.
- Test generation against seeded PostgreSQL data.
- Demonstrate completing a task and deactivating an interest through
  the real API, then generating updated recommendations.
- Demonstrate an empty user against the real data sources.

These integration tasks are deferred for follow-up. The current
fake-data tests do not establish that the real-data demo works.