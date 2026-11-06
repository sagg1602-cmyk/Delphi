# Delphi API

Setup, the schema, and one example request and response for every route are in [HANDOFF.md](HANDOFF.md).

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn main:app --reload --port 8000
pytest
```

The API does not migrate on startup. `X-Dev-User` defaults to `dev-user-1`.
