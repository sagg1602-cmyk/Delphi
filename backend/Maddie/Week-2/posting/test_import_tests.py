"""Tests: import happy path, empty file, binary file, oversized file, correct source fields on the stored note.

Adjust the two lines marked ADJUST so `client` builds your real app (Ava's create_app)
with the import router registered:  app.include_router(notes_import.router)
"""
import pytest
from fastapi.testclient import TestClient

from models import NoteCreate  # noqa: F401  (used to skip the source_path check until the column exists)

# ADJUST 1: where create_app lives
from main import create_app  # noqa: E402


@pytest.fixture()
def client():
    app = create_app()  # ADJUST 2: add test DB / dev-user setup here if your app needs it
    return TestClient(app)


def upload(client, name: str, data: bytes, content_type: str = "text/markdown"):
    return client.post("/notes/import", files={"file": (name, data, content_type)})


def test_happy_path_uses_first_heading(client):
    res = upload(client, "ml-basics.md", b"# Gradient Descent\n\nWalk downhill on the loss surface.\n")
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["title"] == "Gradient Descent"
    assert body["source_type"] == "markdown_import"


def test_title_falls_back_to_file_name(client):
    res = upload(client, "linear-algebra-notes.md", b"No heading here, just text.\n")
    assert res.status_code == 201, res.text
    assert res.json()["title"] == "linear-algebra-notes"


def test_stored_note_has_import_source_fields(client):
    res = upload(client, "week3.md", b"# Week 3\n\nSome content.\n")
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["source_type"] == "markdown_import"
    if "source_path" not in NoteCreate.model_fields:
        pytest.skip("notes has no source_path column yet (waiting on Ava)")
    assert body["source_path"] == "week3.md"


def test_empty_file_is_rejected_cleanly(client):
    res = upload(client, "empty.md", b"")
    assert 400 <= res.status_code < 500
    assert "empty" in res.json()["detail"].lower()


def test_whitespace_only_file_is_rejected(client):
    res = upload(client, "blank.md", b"  \n\n \t\n")
    assert 400 <= res.status_code < 500


def test_binary_file_is_rejected_cleanly(client):
    res = upload(client, "image.md", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00")
    assert 400 <= res.status_code < 500
    assert isinstance(res.json()["detail"], str)
    assert "Traceback" not in res.text


def test_non_utf8_file_is_rejected_cleanly(client):
    res = upload(client, "latin.md", b"# Caf\xe9\n\n\xff\xfe\xfa bad bytes")
    assert 400 <= res.status_code < 500
    assert "Traceback" not in res.text


def test_oversized_file_is_rejected_cleanly(client):
    res = upload(client, "big.md", b"# Big\n\n" + b"a" * 1_100_000)
    assert 400 <= res.status_code < 500
    assert "too large" in res.json()["detail"].lower()


def test_wrong_extension_is_rejected(client):
    res = upload(client, "notes.pdf", b"# Title\n\ntext", "application/pdf")
    assert 400 <= res.status_code < 500
