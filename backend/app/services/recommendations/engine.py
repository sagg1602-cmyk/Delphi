"""Delphi Week 1: deterministic recommendations using synthetic context.

No API calls, database, third-party packages, or model keys are required.
The input/output contract is a draft for review with Manny and Miya.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


# SAMPLE CATALOG ONLY: two real resources, not the final product catalog.
# Titles and destinations checked against the publishers on 2026-10-28.
SAMPLE_CATALOG = [
    {
        "id": "resource_python_tutorial",
        "title": "The Python Tutorial",
        "topics": ["python"],
        "url": "https://docs.python.org/3/tutorial/",
    },
    {
        "id": "resource_postgresql_tutorial",
        "title": "PostgreSQL Tutorial",
        "topics": ["sql", "postgresql", "databases"],
        "url": "https://www.postgresql.org/docs/current/tutorial.html",
    },
]

FIXTURE_DIR = (
    Path(__file__).resolve().parents[4]
    / "shared" / "fixtures" / "recommendations_week1"
)


def _required_text(record, field):
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{field}' must be a non-empty string.")
    return value.strip()


def _read_date(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"{label} must be a date in YYYY-MM-DD format.")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{label} is not a valid calendar date.") from None


def _keywords(text):
    # A small lexical hint, not semantic search or a replacement for Xitlaly's work.
    ignored = {"homework", "assignment", "notes", "study", "work", "with", "this", "that"}
    return {word for word in re.findall(r"[a-z]+", text.lower())
            if len(word) >= 4 and word not in ignored}


def recommend_study(tasks, user_id, today, retrieved_notes):
    """Choose one unfinished dated task; return [] if none qualifies."""
    candidates = []
    for task in tasks:
        if task.get("user_id") != user_id:
            continue
        if not isinstance(task.get("completed", False), bool):
            raise ValueError("Task 'completed' must be true or false.")
        if task.get("completed", False) or not task.get("due_date"):
            continue
        task_id = _required_text(task, "id")
        _required_text(task, "title")
        due = _read_date(task["due_date"], f"Task {task_id} due_date")
        candidates.append((due, task_id, task))

    if not candidates:
        return []

    # IDs settle equal-deadline ties consistently, regardless of input ordering.
    due, task_id, task = min(candidates, key=lambda item: (item[0], item[1]))
    days = (due - today).days
    if days < 0:
        timing = f"was due on {due.isoformat()} and is overdue"
    elif days == 0:
        timing = f"is due today ({due.isoformat()})"
    else:
        unit = "day" if days == 1 else "days"
        timing = f"is due in {days} {unit} ({due.isoformat()})"

    reason = f"This task {timing}. It has the earliest deadline among your unfinished dated tasks."
    evidence_ids = [task_id]
    task_words = _keywords(task["title"])

    # Notes are optional. Cite one only when it is owned by this user, has text,
    # and shares a meaningful keyword with the selected task's title.
    for note in sorted(retrieved_notes, key=lambda item: item.get("id", "")):
        if note.get("user_id") != user_id:
            continue
        text = note.get("excerpt") or note.get("content") or ""
        note_title = note.get("title", "")
        if not text.strip() or not task_words.intersection(_keywords(note_title + " " + text)):
            continue
        note_id = _required_text(note, "id")
        note_title = _required_text(note, "title")
        reason += f' The note "{note_title}" shares a topic keyword with this task.'
        evidence_ids.append(note_id)
        break

    return [{
        "type": "study",
        "title": f"Work on {task['title'].strip()}",
        "reason": reason,
        "evidence_ids": evidence_ids,
        "action_target": task_id,
    }]


def recommend_discovery(interests, catalog):
    """Match the first supported interest to a real resource in the supplied catalog."""
    for interest in interests:
        if not isinstance(interest, str):
            raise ValueError("Each interest must be a string.")
        topic = interest.strip().casefold()
        if not topic:
            continue
        for resource in sorted(catalog, key=lambda item: item["id"]):
            if topic not in [tag.strip().casefold() for tag in resource["topics"]]:
                continue
            return [{
                "type": "discovery",
                "title": f"Explore {resource['title']}",
                "reason": f"This catalog resource matches your stated interest in {interest.strip()}.",
                "evidence_ids": [resource["id"]],
                "action_target": resource["url"],
            }]
    return []


def generate_recommendations(context, catalog=None):
    """Return at most one study and one discovery suggestion, in that order.

    The caller supplies 'today', so the same input always gives the same output.
    A missing match is omitted; no placeholder or invented source is generated.
    """
    if not isinstance(context, dict):
        raise ValueError("Context must be a JSON object.")
    user_id = _required_text(context, "user_id")
    today = _read_date(context.get("today"), "today")
    for field in ("interests", "tasks", "retrieved_notes"):
        if not isinstance(context.get(field, []), list):
            raise ValueError(f"'{field}' must be a list.")
    for field in ("tasks", "retrieved_notes"):
        if not all(isinstance(item, dict) for item in context.get(field, [])):
            raise ValueError(f"Each item in '{field}' must be an object.")

    resources = SAMPLE_CATALOG if catalog is None else catalog
    return (
        recommend_study(context.get("tasks", []), user_id, today,
                        context.get("retrieved_notes", []))
        + recommend_discovery(context.get("interests", []), resources)
    )


def main():
    parser = argparse.ArgumentParser(description="Run the Delphi Week 1 recommendation prototype.")
    parser.add_argument("input", nargs="?", type=Path,
                        default=FIXTURE_DIR / "due_task.input.json")
    parser.add_argument("--output", type=Path, help="Also save the output as a JSON fixture.")
    args = parser.parse_args()
    try:
        context = json.loads(args.input.read_text(encoding="utf-8"))
        rendered = json.dumps(generate_recommendations(context), indent=2) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
