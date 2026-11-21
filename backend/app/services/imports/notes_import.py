"""Draft upload route. It is not registered on the app.

Create a note with POST /notes. The parser lives in markdown_notes.py.
"""

import re
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import ValidationError

from sqlalchemy.engine import Connection

from app.api.deps import get_current_user_id, get_db
from app.repositories.notes import create_note
from app.schemas import NoteCreate, NoteOut
from app.services.imports.markdown_notes import Note, NoteFormatError

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
    if not raw.replace(b"\xef\xbb\xbf", b"", 1).strip():  # empty, or just an invisible BOM
        raise HTTPException(status_code=422, detail=f"{filename}: file is empty")

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


@router.post("/notes/import", status_code=201, response_model=NoteOut)
def import_note(
    file: UploadFile = File(...),
    db: Connection = Depends(get_db),
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
    try:
        body = NoteCreate(**fields)
    except ValidationError as exc:  # e.g. a heading over 200 characters
        problems = "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors())
        raise HTTPException(status_code=422, detail=f"{filename}: {problems}") from exc

    return create_note(
        db,
        user_id,
        body.title,
        body.content,
        body.source_type,
        body.source_path,
    )
