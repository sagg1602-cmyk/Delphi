# Delphi MVP scope — Weeks 1 and 2

Prepared for Sebastian's issues #7 and #18. Audit date: November 13, 2026 (Pacific).
Baseline: main at `f92c15c4f3d39f321d12d338e8c9c4c1ffa1693d`.
This is a proposed consolidation for team review, not a record of meetings or approvals.

## Product promise

A fictional student saves a task and a related note, opens Today to see a useful
study action and a relevant learning resource, and can inspect the real records
behind each suggestion. Completing the task removes its study suggestion on refresh.

## Week 1: separate foundations

Deliver runnable note/task persistence (Ava, #1), identifiable keyword retrieval
(Xitlaly, #2), Markdown-to-structured-note parsing (Maddie, #3), deterministic
recommendation examples (Youssef, #4), and a navigable fixture-based Today page
(Miya, #5). Manny owns technical contracts and setup (#6); Sebastian owns scope,
working-session preparation, blockers, and checkpoint preparation (#7).
Each contributor shows one working prototype in 3–5 minutes. An integrated
browser flow is not a Week 1 completion criterion.

## Week 2: first connected loop

| In scope | Acceptance evidence | Owner / issue |
| --- | --- | --- |
| Stored notes, tasks, active interests and dev-user scoping | Create/read, task completion, second-user isolation | Ava #12 |
| PostgreSQL note retrieval | Ranked real note IDs, deletion exclusion, Recall@5 | Xitlaly #13 |
| Fictional notes, one-file import, catalog and loading | About 25 notes; 20 checked resources; repeatable loader | Maddie #14 |
| Recommendations from stored data | Up to one study and one discovery card, valid evidence, empty user | Youssef #15 |
| Today, Tasks, Notes on live API | Add task/note, inspect Why this?, complete task and refresh | Miya #16 |
| Setup, merge coordination, real smoke test | Clean setup and browser → API → database proof | Manny #17 |
| Scope, handoff checks, status and demo | Reviewed contracts, status record and six-minute walkthrough | Sebastian #18 |

Cut line: ship the five required frontend items in #16 before optional interests UI,
note deletion UI, or search UI. Backend interest/deletion behavior remains in scope.

## Explicitly deferred

Real authentication; saved recommendations; feedback/save/dismiss buttons; LLM
explanations; calendar/free-window logic; notifications and workers; ZIP imports;
full weighted ranking; CI; deployment. No real student data or API keys are needed.
Sebastian's assignment does not include feature implementation unless the tech lead
assigns it. This PR proposes documentation only.

## Release gate

Week 2 is complete only when the live six-step demo in [demo-week2.md](demo-week2.md)
passes and each engineer confirms a done/partial/blocked status. Fixtures demonstrate
components but cannot establish that the connected loop works. See
[week1-week2-status.md](week1-week2-status.md) for the current evidence and blockers.
