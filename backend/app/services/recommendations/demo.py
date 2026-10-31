"""Run all three Week 1 scenarios and verify their main outcomes."""

import argparse
import json

from engine import FIXTURE_DIR, generate_recommendations


def run_demo(write_fixtures=False):
    outputs = {}
    for name in ("due_task", "changed_interest", "no_context"):
        context = json.loads((FIXTURE_DIR / f"{name}.input.json").read_text())
        result = generate_recommendations(context)
        outputs[name] = result
        rendered = json.dumps(result, indent=2) + "\n"
        print(f"\nSCENARIO: {name}\n{rendered}")
        if write_fixtures:
            (FIXTURE_DIR / f"{name}.output.json").write_text(rendered, encoding="utf-8")

    assert outputs["due_task"][0]["action_target"] == "task_calc"
    assert outputs["due_task"][1]["evidence_ids"] == ["resource_python_tutorial"]
    assert outputs["changed_interest"][0] == outputs["due_task"][0]
    assert outputs["changed_interest"][1]["evidence_ids"] == ["resource_postgresql_tutorial"]
    assert outputs["no_context"] == []
    print("PASS: due task, changed interest, and no usable context.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-fixtures", action="store_true",
                        help="Regenerate the three output JSON files for the frontend.")
    run_demo(parser.parse_args().write_fixtures)
