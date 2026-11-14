"""Deterministic Week 2 recommendations.

Context contains:
user_id, today, tasks, interests, retrieved_notes, catalog.

Interests are objects with id, user_id, name, and active.
Resources have id, title, tags, and url.
The context builder adapts teammates' data to this format.
"""

import re
from datetime import date


def keywords(value):
    ignored = {
        "the", "and", "with", "this", "that",
        "homework", "assignment", "notes", "study", "work",
    }
    return {
        word for word in re.findall(r"[a-z0-9]+", value.casefold())
        if len(word) >= 3 and word not in ignored
    }


def read_date(value):
    if value is None or value == "":
        return None
    if type(value) is date:
        return value
    return date.fromisoformat(value)


def stable_id(record):
    return str(record["id"])


def evidence(kind, record, label_field="title"):
    return {
        "type": kind,
        "id": record["id"],
        "label": record[label_field],
    }


def best_note(text, notes):
    words = keywords(text)
    matches = []
    for note in notes:
        content = note.get("excerpt") or note.get("content") or ""
        score = len(words & keywords(note["title"] + " " + content))
        if score:
            matches.append((score, note))
    matches.sort(key=lambda item: (-item[0], stable_id(item[1])))
    return matches[0] if matches else (0, None)


def timing(due, today):
    if due is None:
        return "has no deadline set"
    days = (due - today).days
    if days < 0:
        return f"is overdue by {abs(days)} day(s)"
    if days == 0:
        return "is due today"
    return f"is due in {days} day(s)"


def validate_evidence(recommendations, context):
    """Reject evidence outside the supplied input and invented URLs."""
    collections = {
        "task": context.get("tasks", []),
        "note": context.get("retrieved_notes", []),
        "interest": context.get("interests", []),
        "resource": context.get("catalog", []),
    }
    allowed = {
        (kind, type(item["id"]), item["id"])
        for kind, items in collections.items()
        for item in items
    }
    for recommendation in recommendations:
        for item in recommendation["evidence"]:
            key = (item["type"], type(item["id"]), item["id"])
            if key not in allowed:
                raise ValueError("Evidence ID was not in the input context.")

        if recommendation["type"] == "discovery":
            resource_ids = {
                item["id"] for item in recommendation["evidence"]
                if item["type"] == "resource"
            }
            urls = {
                resource["url"]
                for resource in context.get("catalog", [])
                if resource["id"] in resource_ids
            }
            if recommendation["action"]["target"] not in urls:
                raise ValueError("Discovery URL must match its catalog evidence.")


def generate_recommendations(context):
    """Return up to one study and one discovery recommendation."""
    user_id = context["user_id"]
    today = read_date(context["today"])
    if today is None:
        raise ValueError("Context must include today's date.")

    notes = [
        note for note in context.get("retrieved_notes", [])
        if note.get("user_id") == user_id
    ]
    tasks = [
        task for task in context.get("tasks", [])
        if task.get("user_id") == user_id
        and task.get("status", "todo") in {"todo", "in_progress"}
        and not task.get("completed", False)
    ]
    interests = [
        interest for interest in context.get("interests", [])
        if interest.get("user_id") == user_id
        and interest.get("active") is True
        and interest.get("name", "").strip()
    ]

    recommendations = []

    # Earlier deadlines first; related notes break equal-deadline ties.
    # Undated tasks follow dated tasks. IDs settle remaining ties.
    study_candidates = []
    for task in tasks:
        due = read_date(task.get("due_date"))
        _, note = best_note(task["title"], notes)
        study_candidates.append((task, due, note))

    study_candidates.sort(
        key=lambda item: (
            item[1] or date.max,
            item[2] is None,
            stable_id(item[0]),
        )
    )

    if study_candidates:
        task, due, note = study_candidates[0]
        reason = f'{task["title"]} {timing(due, today)}.'
        items = [evidence("task", task)]
        if note:
            reason += (
                f' Your note "{note["title"]}" shares topic keywords'
                " and may help you get started."
            )
            items.append(evidence("note", note))

        recommendations.append({
            "id": f'study-{task["id"]}',
            "type": "study",
            "title": f'Work on {task["title"]}',
            "reason": reason,
            # A suggested study session, not a completion-time prediction.
            "estimated_minutes": 25,
            "evidence": items,
            "action": {"type": "open_task", "target": task["id"]},
        })

    discovery_candidates = []
    for resource in context.get("catalog", []):
        tags = {tag.strip().casefold() for tag in resource.get("tags", [])}
        matched = sorted(
            [
                interest for interest in interests
                if interest["name"].strip().casefold() in tags
            ],
            key=stable_id,
        )
        if not matched or not resource.get("url"):
            continue

        overlap = len({
            interest["name"].strip().casefold() for interest in matched
        })
        score, note = best_note(
            resource["title"] + " " + " ".join(sorted(tags)), notes
        )
        discovery_candidates.append(
            (overlap, score, resource, matched, note)
        )

    discovery_candidates.sort(
        key=lambda item: (-item[0], -item[1], stable_id(item[2]))
    )

    if discovery_candidates:
        _, _, resource, matched, note = discovery_candidates[0]
        names = ", ".join(interest["name"] for interest in matched)
        reason = f'This catalog resource matches your active interests: {names}.'
        items = [
            evidence("interest", interest, "name") for interest in matched
        ]
        items.append(evidence("resource", resource))
        if note:
            reason += f' It also shares topic keywords with "{note["title"]}".'
            items.append(evidence("note", note))

        recommendations.append({
            "id": f'discovery-{resource["id"]}',
            "type": "discovery",
            "title": f'Explore {resource["title"]}',
            "reason": reason,
            # A suggested exploration session.
            "estimated_minutes": 15,
            "evidence": items,
            "action": {"type": "open_url", "target": resource["url"]},
        })

    validate_evidence(recommendations, context)
    return recommendations