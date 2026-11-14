# Sample Import: Student Notes Dataset

## Schema (shared with Xitlaly and Ava)
Each note is a plain `.md` file:

    # Title        <- line 1: one '#', then the title
    1              <- line 2: the note ID, a whole number only
                   <- blank line (optional)
    Content...     <- line 3+: the note body

## Dataset
- `notes/`: 10 fictional student notes on distinct topics (IDs 1-10)
- `bad_samples/`: `empty.md`, `invalid_binary.md` (non-text bytes), `missing_id.md` (schema error)

## Sample import
From this folder run:

    python NoteReqDraft.py

Or in code:

    from NoteReqDraft import Note, load_folder

    note = Note.mdReader("notes/note_01_photosynthesis")   # .md optional
    print(note.title, note.ID)          # Photosynthesis 1
    print(note.to_dict())               # ready to send to Ava's API in Week 2

    notes, errors = load_folder("notes")  # 10 notes, 0 errors

## Expected behavior on bad files
| File | Result |
|---|---|
| empty.md | NoteFormatError: file is empty |
| invalid_binary.md | NoteFormatError: not a text file |
| missing_id.md | NoteFormatError: line 2 must be the note ID |
| nonexistent file | FileNotFoundError |

`load_folder()` skips bad files and returns them in an `errors` list instead of crashing.
