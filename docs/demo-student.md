# Fictional demo student

Proposed shared persona for #7, #14 and #18: Alex, a fictional student taking
introductory computer science, economics and statistics. No real student data.
Maddie and Xitlaly should confirm this proposal against their expanded dataset.

## Data alignment

| Item | Value / source | Expected role |
| --- | --- | --- |
| Active interest | `Python` | Match catalog tag `python` |
| Primary task | `Practice binary search in Python`; due two days after rehearsal; 25 minutes; `todo` | Study candidate |
| Supporting note | Existing `backend/Maddie/Week 1/notes/note_03_binary_search.md` (file ID 3) | Evidence from a real saved note |
| Secondary task | `Review linear regression residuals`; due five days after rehearsal | Later-deadline comparison |
| Secondary note | Existing `note_07_linear_regression.md` (file ID 7) | Same student's statistics coursework |
| Secondary interest | `Data science` | Future catalog overlap after resources are reviewed |
| Discovery resource | The Python Tutorial, `https://docs.python.org/3/tutorial/` | Existing recommendation fixture candidate; not a substitute for Maddie's checked catalog |

Create all records under the same development user. Use returned database IDs in
evidence, not file IDs 3/7 or assumed ID 1. Resource and interest IDs must also
come from the loaded context. Add a fresh manual note with title
`Binary search practice` and content `Binary search halves a sorted list on each step.`
when rehearsing the browser capture flow.

## Rehearsal rules

Compute due dates relative to the actual rehearsal; avoid the expired fixed
November 6 fixture date in a live demo. The existing engine demo intentionally
uses a fixed `today` for reproducibility; label it synthetic. The first demo task
must be the earliest unfinished task or the deterministic engine may choose another.
Use an isolated local demo database/user, and record created IDs. Re-running a
loader should skip an existing title for that user as #14 requires.

After completion, expect no study recommendation for that task; another eligible
task may become the study card. Discovery can remain. A second user with no tasks,
interests or notes must return an empty list through the real endpoint once user
scoping is restored. Main's fixed user dependency cannot currently prove this.
