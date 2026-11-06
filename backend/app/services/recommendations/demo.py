"""Demonstrate Week 2 recommendations using fake data.

Run from the repository root:
python -m backend.app.services.recommendations.demo
"""

import json
from copy import deepcopy
from datetime import date

from .context import build_user_context
from .engine import generate_recommendations
from .fake_sources import FakeSources


def run_scenario(name, sample, expected_types, user_id=1):
    sources = FakeSources(sample)
    context = build_user_context(
        db=None,
        user_id=user_id,
        sources=sources,
        today=date.fromisoformat(sample["today"]),
    )
    result = generate_recommendations(context)

    assert [item["type"] for item in result] == expected_types
    print(f"\nSCENARIO: {name}")
    print(json.dumps(
        {"recommendations": result},
        indent=2,
        ensure_ascii=False,
    ))
    return result


def run_demo():
    original = FakeSources.from_fixture().context

    run_scenario(
        "Due task and active interest",
        original,
        ["study", "discovery"],
    )

    changed = deepcopy(original)
    changed["interests"][0]["name"] = "SQL"
    changed["catalog"].append({
        "id": "resource_sql",
        "title": "PostgreSQL Tutorial",
        "tags": ["sql"],
        "url": "https://www.postgresql.org/docs/current/tutorial.html",
    })
    result = run_scenario(
        "Changed interest", changed, ["study", "discovery"]
    )
    assert result[1]["id"] == "discovery-resource_sql"

    completed = deepcopy(original)
    completed["tasks"][0]["status"] = "done"
    run_scenario("Completed task", completed, ["discovery"])

    cancelled = deepcopy(original)
    cancelled["tasks"][0]["status"] = "cancelled"
    run_scenario("Cancelled task", cancelled, ["discovery"])

    inactive = deepcopy(original)
    inactive["interests"][0]["active"] = False
    run_scenario("Deactivated interest", inactive, ["study"])

    no_notes = deepcopy(original)
    no_notes["retrieved_notes"] = []
    result = run_scenario(
        "No notes", no_notes, ["study", "discovery"]
    )
    assert all(
        item["type"] != "note"
        for item in result[0]["evidence"]
    )

    no_tasks = deepcopy(original)
    no_tasks["tasks"] = []
    run_scenario("No tasks", no_tasks, ["discovery"])

    run_scenario("Empty user", original, [], user_id=999)

    print("\nPASS: all eight fake-data scenarios.")
    print("Real database integration is not demonstrated here.")


if __name__ == "__main__":
    run_demo()