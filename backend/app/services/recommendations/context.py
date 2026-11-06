"""Gather and normalize the input for the recommendation engine.

The sources adapter connects to task, interest, retrieval, and catalog
helpers. Tests can supply a fake adapter without using a database.
"""

from datetime import date


def build_user_context(db, user_id, *, sources, today=None):
    """Build context using the supplied data-source adapter.

    Adapter methods:
      list_tasks(db, user_id)
      list_interests(db, user_id)
      retrieve_notes(db, user_id, tasks, interests)
      load_catalog()

    These are our adapter's methods, not assumptions about teammates'
    final function names. The adapter translates their interfaces.
    """
    current_date = today if today is not None else date.today()

    tasks = [
        dict(task)
        for task in sources.list_tasks(db, user_id)
        if task.get("user_id") == user_id
        and task.get("status", "todo") in {"todo", "in_progress"}
        and not task.get("completed", False)
    ]

    interests = [
        dict(interest)
        for interest in sources.list_interests(db, user_id)
        if interest.get("user_id") == user_id
        and interest.get("active") is True
        and interest.get("name", "").strip()
    ]

    active_names = {
        interest["name"].strip().casefold()
        for interest in interests
    }

    catalog = []
    if active_names:
        for resource in sources.load_catalog():
            tags = {
                tag.strip().casefold()
                for tag in resource.get("tags", [])
            }
            if tags & active_names:
                catalog.append(dict(resource))

    notes = []
    if tasks or interests:
        notes = [
            dict(note)
            for note in sources.retrieve_notes(
                db, user_id, tasks, interests
            )
            if note.get("user_id") == user_id
        ]

    return {
        "user_id": user_id,
        "today": current_date.isoformat(),
        "tasks": tasks,
        "interests": interests,
        "retrieved_notes": notes,
        "catalog": catalog,
    }