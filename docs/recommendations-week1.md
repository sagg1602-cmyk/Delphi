# Week 1 Recommendation Engine

## Overview

This Python prototype uses student tasks, interests, and optional retrieved notes to generate up to two recommendations:

- A study suggestion based on the earliest unfinished task deadline.
- A discovery suggestion matching an interest to a resource in a small sample catalog.

The prototype runs on fictional student data using deterministic rules. The same input produces the same output.

## Run

Run these commands from the Delphi repository root.

Show one example:

```bash
python3 backend/app/services/recommendations/engine.py
```

Show all three demonstration scenarios:

```bash
python3 backend/app/services/recommendations/demo.py
```

Run the automated tests:

```bash
python3 -m unittest discover -s backend/app/services/recommendations -p 'test_*.py' -v
```

No additional Python packages or API keys are required.

## Input

The function `generate_recommendations(context, catalog=None)` accepts:

- `user_id`: the student's ID.
- `today`: a reference date in YYYY-MM-DD format.
- `interests`: a list of interest strings, such as `"python"`.
- `tasks`: task records containing `id`, `user_id`, `title`, `due_date`, and `completed`.
- `retrieved_notes`: optional note records containing `id`, `user_id`, `title`, and `excerpt`. Full `content` can be used instead of an excerpt.

The reference date is supplied explicitly so the examples remain reproducible. The fixtures use October 28, 2026.

The input format is proposed and needs confirmation with the backend and memory teams.

## Recommendation rules

### Study

The engine ignores completed tasks, tasks without deadlines, and tasks belonging to a different user. It selects the remaining task with the earliest deadline, including overdue tasks. Equal deadlines are resolved alphabetically by task ID.

The explanation states the deadline relative to the supplied reference date.

A supplied note may be included as evidence if it belongs to the same user and shares a meaningful keyword with the task title. This is a basic keyword check.

### Discovery

The engine matches interests against the sample catalog's topic tags, ignoring capitalization and surrounding spaces.

It selects the first interest with a matching resource. The sample catalog contains the official Python tutorial and PostgreSQL tutorial.

### No usable context

If neither category has supporting information, the result is an empty list. If only one category has support, only that recommendation is returned.

## Output

The output is a JSON array. Each recommendation contains:

- `type`: `"study"` or `"discovery"`.
- `title`: the card heading.
- `reason`: the explanation.
- `evidence_ids`: supporting task, note, or resource IDs.
- `action_target`: a task ID for study or a catalog URL for discovery.

The action-target convention needs confirmation with the frontend team.

## Demonstration scenarios

The input and output examples are in:

`shared/fixtures/recommendations_week1/`

1. `due_task`: calculus homework due October 30 is selected before economics reading due November 2. A Python interest produces a Python resource suggestion.
2. `changed_interest`: changing the interest to SQL changes the discovery resource while keeping the study suggestion unchanged.
3. `no_context`: empty tasks, interests, and notes produce an empty array.

Miya and Manny can use `due_task.output.json` as the example containing both recommendation types.

## Testing

The 18 automated tests cover deadline ordering, completed tasks, optional notes, changed interests, empty results, evidence references, invalid dates, and repeatable output.

The demo and all 18 tests passed locally.

## Limitations and next steps

The prototype uses synthetic data, simple deadline ordering, basic note keyword matching, and a two-resource sample catalog. Tasks without deadlines are currently omitted.

It does not yet connect to the database, retrieval service, or frontend. It does not use live LLM calls or learn from feedback.

The next step is to confirm field names with the team, connect stored tasks and retrieved notes to the function, and display the generated recommendations on the Today page.