# Fictional notes

These files are sample student notes, not application code.

Each note is a plain `.md` file:

```
# Title
1

Content...
```

Line 2 is the file's own number. The API assigns the database id when the note is saved.

- `notes/`: 25 fictional notes, numbered 1–25
- `bad_samples/`: `empty.md`, `invalid_binary.md`, and `missing_id.md`

The parser is `app/services/imports/markdown_notes.py`. To post the notes through the API, from `backend/` with the server running:

```bash
python -m app.services.imports.load_notes
```
