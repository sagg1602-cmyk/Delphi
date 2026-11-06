"""Retrieval tests on delphi_test. Run from backend/: python -m pytest tests/test_retrieval.py -v"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import DEV_USER_ID, init_schema, make_engine
from app.main import create_app
from app.repositories.notes import create_note
from app.services.memory.retrieval import build_task_query, retrieve_notes
from app.services.memory.sample_data import insert_sample_notes
from app.services.memory.sample_data import test_database_url as get_test_url

ALEX = 501
SAM = 502


@pytest.fixture(scope="module")
def engine():
    eng = make_engine(get_test_url())
    init_schema(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def db(engine):
    with engine.connect() as conn:
        tx = conn.begin()
        conn.execute(text(
            "INSERT INTO users (id, name) VALUES (:a, 'alex test'), (:s, 'sam test') "
            "ON CONFLICT (id) DO NOTHING"
        ), {"a": ALEX, "s": SAM})
        conn.ids = insert_sample_notes(conn, ALEX)
        yield conn
        tx.rollback()


def top_id(db, query):
    results = retrieve_notes(db, ALEX, query)
    return results[0]["note_id"] if results else None


def test_photosynthesis_query(db):
    assert top_id(db, "calvin cycle in the chloroplast") == db.ids[1]


def test_task_title_with_extra_words_still_matches(db):
    assert top_id(db, "Draft essay intro on revenge and madness") == db.ids[8]


def test_physics_query(db):
    assert top_id(db, "net force and acceleration") == db.ids[5]


def test_title_ranks_above_content(db):
    title_hit = create_note(db, ALEX, "Recursion basics", "Base case first.", "manual")
    content_hit = create_note(db, ALEX, "CS lecture 4", "Today we covered recursion.", "manual")
    ids = [r["note_id"] for r in retrieve_notes(db, ALEX, "recursion")]
    assert ids.index(title_hit["id"]) < ids.index(content_hit["id"])


def test_result_shape_and_score_range(db):
    result = retrieve_notes(db, ALEX, "binary search")[0]
    assert set(result) >= {"note_id", "title", "excerpt", "score", "source_type"}
    assert 0 < result["score"] < 1
    assert result["excerpt"]


def test_limit(db):
    assert len(retrieve_notes(db, ALEX, "the plates cells force price light", limit=2)) == 2


def test_other_user_never_sees_alex_notes(db):
    assert retrieve_notes(db, SAM, "photosynthesis calvin cycle") == []
    sams = create_note(db, SAM, "Photosynthesis quiz", "Sam's own notes.", "manual")
    ids = [r["note_id"] for r in retrieve_notes(db, SAM, "photosynthesis")]
    assert ids == [sams["id"]]


def test_deleted_note_disappears(db):
    note_id = db.ids[10]
    assert top_id(db, "plate tectonics") == note_id
    db.execute(text("DELETE FROM notes WHERE id = :id"), {"id": note_id})
    assert note_id not in [r["note_id"] for r in retrieve_notes(db, ALEX, "plate tectonics")]


def test_no_match_returns_empty_list(db):
    assert retrieve_notes(db, ALEX, "quantum chromodynamics") == []


def test_only_stopwords_returns_empty_list(db):
    assert retrieve_notes(db, ALEX, "the and of") == []
    assert retrieve_notes(db, ALEX, "") == []


def test_punctuation_does_not_crash(db):
    assert isinstance(retrieve_notes(db, ALEX, "F = ma?! (Newton's) & | !"), list)


def test_build_task_query():
    query = build_task_query(
        "Draft research introduction",
        [{"name": "cognition", "active": True}, {"name": "chess", "active": False}],
    )
    assert query == "draft research introduction cognition"


def test_search_route(engine):
    with engine.begin() as conn:
        note = create_note(conn, DEV_USER_ID, "Zebrafish lab", "Zebrafish embryo imaging.", "manual")
    try:
        with TestClient(create_app(engine)) as client:
            response = client.get("/notes/search", params={"q": "zebrafish", "limit": 5})
            assert response.status_code == 200
            assert response.json()[0]["note_id"] == note["id"]
            assert client.get("/notes/search", params={"q": "nothingmatchesthis"}).json() == []
    finally:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM notes WHERE id = :id"), {"id": note["id"]})
