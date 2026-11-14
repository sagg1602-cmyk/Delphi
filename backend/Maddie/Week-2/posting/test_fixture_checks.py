"""Fixture checks: sample notes and the resource catalog must match the agreed shapes."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import pytest


def _fixtures_dir() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "shared" / "fixtures").is_dir():
            return parent / "shared" / "fixtures"
    raise FileNotFoundError("shared/fixtures not found above " + str(here))


FIXTURES = _fixtures_dir()
NOTE_FILES = sorted(FIXTURES.glob("note_*.md"))
RESOURCES_FILE = FIXTURES / "resources.json"

RESOURCE_FIELDS = {"id", "title", "url", "description", "content_type", "estimated_minutes", "tags"}


def _read_note(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    return {"lines": lines, "title": lines[0][2:].strip() if lines else ""}


# ---------- notes ----------

def test_there_are_sample_notes():
    assert len(NOTE_FILES) >= 25, f"expected ~25 sample notes, found {len(NOTE_FILES)}"


@pytest.mark.parametrize("path", NOTE_FILES, ids=lambda p: p.name)
def test_note_shape(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines and lines[0].startswith("# ") and lines[0][2:].strip(), "line 1 must be '# Title'"
    assert len(lines) >= 3, "needs title, note-number line, blank line, body"
    assert lines[1].strip().isdigit(), "line 2 must be the note number"
    assert lines[2].strip() == "", "line 3 must be blank"
    body = [l for l in lines[3:] if l.strip()]
    assert len(body) == 3, f"body should be three lines, found {len(body)}"
    m = re.fullmatch(r"note_0*(\d+)\.md", path.name)
    if m:
        assert int(lines[1]) == int(m.group(1)), "note number should match the file name"


def test_note_titles_and_numbers_unique():
    titles, numbers = {}, {}
    for p in NOTE_FILES:
        lines = p.read_text(encoding="utf-8").splitlines()
        t = " ".join(lines[0][2:].split()).casefold()
        assert t not in titles, f"{p.name} repeats the title of {titles[t]}"
        titles[t] = p.name
        n = int(lines[1])
        assert n not in numbers, f"{p.name} repeats note number {n} from {numbers[n]}"
        numbers[n] = p.name


# ---------- resources ----------

@pytest.fixture(scope="module")
def resources():
    data = json.loads(RESOURCES_FILE.read_text(encoding="utf-8"))
    assert isinstance(data, list), "resources.json must be a list"
    return data


def test_at_least_20_resources(resources):
    assert len(resources) >= 20


def test_resource_required_fields_and_types(resources):
    for r in resources:
        missing = RESOURCE_FIELDS - r.keys()
        assert not missing, f"{r.get('id', r)}: missing {sorted(missing)}"
        for f in ("title", "description", "content_type"):
            assert isinstance(r[f], str) and r[f].strip(), f"{r['id']}: {f} must be non-empty text"
        assert isinstance(r["estimated_minutes"], int) and r["estimated_minutes"] > 0, \
            f"{r['id']}: estimated_minutes must be a positive integer"
        assert isinstance(r["tags"], list) and r["tags"], f"{r['id']}: tags must be a non-empty list"
        assert all(isinstance(t, str) and t.strip() for t in r["tags"]), f"{r['id']}: tags must be text"


def test_resource_ids_unique(resources):
    ids = [r["id"] for r in resources]
    assert len(ids) == len(set(ids)), "duplicate resource ids"


def test_resource_urls_valid_and_unique(resources):
    seen = set()
    for r in resources:
        u = urlparse(r["url"])
        assert u.scheme in {"http", "https"} and u.netloc, f"{r['id']}: bad URL {r['url']!r}"
        assert r["url"] not in seen, f"{r['id']}: duplicate URL"
        seen.add(r["url"])
