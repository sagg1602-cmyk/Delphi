"""
Note loader: reads a plain .md file into a structured Note object.

Shared note schema (agreed with Xitlaly and Ava)
------------------------------------------------
Line 1 : "# Title"        -> one '#' followed by the title
Line 2 : the note ID      -> a whole number, nothing else on the line
Line 3+: note content     -> everything after (a blank line after the ID is skipped)

Example file:

    # Photosynthesis
    1

    Plants turn light, water and CO2 into glucose and oxygen.

Problem files do not crash a batch import: a single file raises NoteFormatError
(or FileNotFoundError), and load_folder() collects those into an error list.
"""

from pathlib import Path


class NoteFormatError(ValueError):
    """Raised when a file can't be turned into a Note (empty, not text, bad schema)."""


class Note:
    def __init__(self, title, ID, content):
        self.title = title
        self.ID = ID
        self.content = content

    def __repr__(self):
        return f"Note(ID={self.ID}, title={self.title!r}, {len(self.content)} chars)"

    def to_dict(self):
        """Plain dict, handy for handing off to Ava's API in Week 2."""
        return {"id": self.ID, "title": self.title, "content": self.content}

    @classmethod
    def mdReader(cls, FileTitle):
        """Load a note from FileTitle (with or without the .md extension)."""
        path = Path(FileTitle)
        if path.suffix != ".md":
            path = path.with_name(path.name + ".md")

        if not path.is_file():
            raise FileNotFoundError(f"No such note file: {path}")

        # Read raw bytes first so non-text files get a clear error
        raw = path.read_bytes()
        if not raw.strip():
            raise NoteFormatError(f"{path.name}: file is empty")
        if b"\x00" in raw:
            raise NoteFormatError(f"{path.name}: not a text file (binary data found)")
        try:
            text = raw.decode("utf-8-sig")  # utf-8-sig also strips a BOM if present
        except UnicodeDecodeError:
            raise NoteFormatError(f"{path.name}: not valid UTF-8 text")

        lines = text.splitlines()

        # Line 1: title
        first = lines[0].strip()
        if not first.startswith("# ") or not first[2:].strip():
            raise NoteFormatError(
                f"{path.name}: line 1 must be a title like '# My Title'"
            )
        title = first[2:].strip()  # drop the '#' so only the title text is kept

        # Line 2: ID
        if len(lines) < 2 or not lines[1].strip().isdigit():
            raise NoteFormatError(
                f"{path.name}: line 2 must be the note ID (a whole number only)"
            )
        ID = int(lines[1].strip())

        # Line 3+: content
        content = "\n".join(lines[2:]).strip()

        return cls(title, ID, content)


def load_folder(folder):
    """Load every .md file in a folder.

    Returns (notes, errors): good notes, plus a list of (filename, message)
    for files that were skipped.
    """
    notes, errors = [], []
    for path in sorted(Path(folder).glob("*.md")):
        try:
            notes.append(Note.mdReader(path))
        except (NoteFormatError, FileNotFoundError) as e:
            errors.append((path.name, str(e)))
    return notes, errors


if __name__ == "__main__":
    here = Path(__file__).parent

    print("--- Sample import: notes/ ---")
    notes, errors = load_folder(here / "notes")
    for n in notes:
        print(n)
    print(f"Loaded {len(notes)} notes, {len(errors)} errors\n")

    print("--- Edge cases: bad_samples/ ---")
    notes, errors = load_folder(here / "bad_samples")
    for name, msg in errors:
        print("SKIPPED ->", msg)
