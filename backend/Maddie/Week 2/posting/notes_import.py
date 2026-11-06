"""POST /notes/import: save one uploaded Markdown file as a note.

Parsing uses the Week 1 loader (Note.mdReader in Maddie/Week 1/NoteReqDraft.py).
Saving goes through Ava's create_note route function, so there is no SQL here.
"""

import importlib.util
import json
import re
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from pydantic import ValidationError

from database import get_current_user_id
from models import NoteCreate, NoteOut

# Load the Week 1 loader straight from where it already lives (its folder name has a space).
_LOADER_PATH = Path(__file__).resolve().parent / "Maddie" / "Week 1" / "NoteReqDraft.py"
_spec = importlib.util.spec_from_file_location("note_req_draft", _LOADER_PATH)
_loader = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_loader)
Note, NoteFormatError = _loader.Note, _loader.NoteFormatError

router = APIRouter()

MAX_UPLOAD_BYTES = 1_000_000
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")


def _as_text(raw: bytes) -> str | None:
    """Decoded text, or None if the file is empty, binary or not UTF-8."""
    if not raw.strip() or b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None


def parse_markdown(raw: bytes, filename: str) -> tuple[str, str]:
    """Return (title, content) for an uploaded Markdown file.

    A file in the shared note layout ('# Title', then the note ID) goes through
    the Week 1 loader. Any other readable Markdown takes its title from the
    first heading, and from the file name if there is no heading.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "upload.md"  # fixed name: the loader needs a .md path
        path.write_bytes(raw)
        try:
            note = Note.mdReader(path)
            return note.title, note.content
        except NoteFormatError as exc:
            text = _as_text(raw)
            if text is None:  # empty, binary or not UTF-8: not a note at all
                detail = str(exc).replace("upload.md", filename)
                raise HTTPException(status_code=422, detail=detail) from exc
            for line in text.splitlines():
                match = HEADING.match(line)
                if match:
                    return match.group(1), text.strip()
            return Path(filename).stem, text.strip()


def _find_create_note(request: Request):
    """Ava's create_note is defined inside create_app(), so look it up on the app."""
    for route in request.app.routes:
        if getattr(route, "path", None) == "/notes" and "POST" in getattr(route, "methods", ()):
            return route.endpoint
    raise HTTPException(status_code=500, detail="POST /notes is not registered")


@router.post("/notes/import", status_code=201, response_model=NoteOut)
def import_note(
    request: Request,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    filename = Path(file.filename or "").name or "upload.md"
    if Path(filename).suffix.lower() not in {".md", ".markdown"}:
        raise HTTPException(status_code=422, detail="Upload a Markdown file (.md or .markdown).")

    raw = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is too large (1 MB limit).")

    title, content = parse_markdown(raw, filename)

    fields = {
        "title": title,
        "content": content,
        "source_type": "markdown_import",
        "source_path": filename,
    }
    if "source_path" not in NoteCreate.model_fields:
        # TODO(Ava): notes has no source_path column yet. Delete this check once it does.
        fields.pop("source_path")

    try:
        body = NoteCreate(**fields)
    except ValidationError as exc:  # e.g. a heading longer than 200 characters
        raise HTTPException(status_code=422, detail=json.loads(exc.json(include_url=False))) from exc

    return _find_create_note(request)(body=body, request=request, user_id=user_id)
