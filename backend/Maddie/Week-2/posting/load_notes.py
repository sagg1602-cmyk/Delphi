#!/usr/bin/env python3
"""Load the fixture notes into the Delphi API through POST /notes.

Safe to run more than once: it first reads GET /notes and skips any note whose
title already exists for the user (the API only lists the dev user's notes).

Usage (from the repo root, with the API running):
    python load_notes.py
    python load_notes.py --base-url http://localhost:8000 --fixtures shared/fixtures
    python load_notes.py --dry-run
    python load_notes.py --header "X-Dev-User: 1"      # only if the API ever needs one
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


def parse_note(path: Path) -> dict:
    """Fixture format: '# Title', a note-number line, a blank line, then the body."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"{path.name}: first line must be '# Title'")
    title = lines[0][2:].strip()
    body = lines[1:]
    if body and body[0].strip().isdigit():  # drop the note-number line
        body = body[1:]
    content = "\n".join(body).strip()
    if not title:
        raise ValueError(f"{path.name}: empty title")
    return {"title": title, "content": content, "source_type": "manual"}


def call(method: str, url: str, headers: dict, payload: dict | None = None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for k, v in headers.items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def norm(title: str) -> str:
    return " ".join(title.split()).casefold()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", default="http://localhost:8000")
    ap.add_argument("--fixtures", default="shared/fixtures")
    ap.add_argument("--header", action="append", default=[], metavar="'Name: value'",
                    help="extra request header (repeatable)")
    ap.add_argument("--dry-run", action="store_true", help="show what would be posted, post nothing")
    args = ap.parse_args()

    headers = {}
    for h in args.header:
        name, _, value = h.partition(":")
        headers[name.strip()] = value.strip()

    files = sorted(Path(args.fixtures).glob("note_*.md"))
    if not files:
        print(f"No note_*.md files found in {args.fixtures}", file=sys.stderr)
        return 1
    notes = [parse_note(f) for f in files]

    base = args.base_url.rstrip("/")
    try:
        _, existing = call("GET", f"{base}/notes", headers)
    except (urllib.error.URLError, OSError) as exc:
        print(f"Could not reach {base}/notes: {exc}", file=sys.stderr)
        return 1
    seen = {norm(n["title"]) for n in existing}

    created = skipped = failed = 0
    for note in notes:
        key = norm(note["title"])
        if key in seen:
            print(f"skip    {note['title']}")
            skipped += 1
            continue
        if args.dry_run:
            print(f"would post  {note['title']}")
            continue
        try:
            status, saved = call("POST", f"{base}/notes", headers, note)
            print(f"created {note['title']}  (id {saved.get('id')}, HTTP {status})")
            seen.add(key)  # also guards against duplicate titles within one run
            created += 1
        except urllib.error.HTTPError as exc:
            print(f"FAILED  {note['title']}: HTTP {exc.code} {exc.read().decode()[:200]}", file=sys.stderr)
            failed += 1
        except (urllib.error.URLError, OSError) as exc:
            print(f"FAILED  {note['title']}: {exc}", file=sys.stderr)
            failed += 1

    print(f"\nDone: {created} created, {skipped} skipped, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
