# Weeks 1–2 status and blockers

Repository audit: November 13, 2026 (Pacific), main `f92c15c`.
These are repository-based assessments, not engineer self-reports or proof that
historical meetings occurred. Original deadlines were October 30 (#7) and
November 6 (#18); this document does not backdate completion.

## Engineer status

| Owner | Assessment | Evidence | Next integration / Week 3 step |
| --- | --- | --- | --- |
| Ava | Partial in current main | #1/#12 closed; #9/#20 merged, but current main still uses schema.sql and fixed user 1; no interests, PATCH tasks, source_path or Alembic | Reconcile `ava/week2-api` onto current main without losing retrieval/recommendations; then verify persistence and isolation |
| Xitlaly | Done as merged component; runtime not reverified here | #2/#13 closed through #21/#22; PostgreSQL retrieval, query helper, route and ten-scenario recall script exist | Run against expanded Maddie dataset and restored deletion/user routes; pass adapter mapping to Youssef |
| Maddie | Partial | #11 merged; ten Markdown samples and parser on main; #14 checks some items complete but expanded set, loader, import endpoint and catalog absent from main | Submit missing work through PR; demonstrate parse → persistence → search; validate catalog and fixtures |
| Youssef | Partial | #19 merged; 16 engine tests and eight synthetic scenarios passed in this audit; #15 remains open; router not registered, real sources absent | Connect real sources/catalog and verify completion, interest deactivation and empty-user scenarios |
| Miya | Blocked from integrated demo; branch work exists | `miya/frontend` contains Next.js prototype; frontend on main only has placeholder; #5/#16 open; old recommendation type on branch | Submit foundation PR, align types and wire required live flows after API readiness |

Manny (#17): partial integration setup; review reconciliation first and own the real
smoke test. Sebastian (#7/#18): scope, handoff comparison, proposed persona,
checkpoint agenda and demo script supplied here; meetings, engineer confirmations
and the connected rehearsal remain unverified.

## Unfinished work

The component prototypes are ahead of the connected application. Backend issue #12
is closed but its Week 2 routes are not in current main. Retrieval exists, but the
public API cannot yet demonstrate task completion, note deletion or a distinct
header-selected user. Recommendations work with synthetic context and still need
a real adapter and catalog. The ten-note dataset is merged; the larger dataset and
resource catalog are not visible on main. The frontend remains on a separate branch
and expects an older card shape. These gaps prevent claiming the Week 2 end-to-end
definition of done; no teammate confirmation is inferred from issue checkboxes.

## Blockers and dependency order

| Priority | Blocker | Owner | Evidence required to clear |
| --- | --- | --- | --- |
| 1 | Closed backend issue differs from main | Ava + Manny | Focused reconciliation PR and passing live route/isolation checks |
| 2 | Expanded fixtures, import and catalog not merged | Maddie | Runnable PR, repeatable loader, URL/shape validation |
| 3 | Recommendation context not backed by real sources | Youssef, with Xitlaly | Registered endpoint returns traceable evidence; completed task disappears |
| 4 | Frontend unavailable on main / old card shape | Miya | Reviewed foundation PR then live wiring PR |
| 5 | No connected-demo evidence or confirmed team status | Manny + Sebastian | Run log/screenshots and contributor done/partial/blocked confirmations |

Work can proceed in parallel on fixtures and frontend types. Merge order remains:
restore core API → fixtures/retrieval compatibility → real recommendations → live
frontend → smoke test and rehearsal. Shared schema changes need consumer review.

## Week 1 housekeeping

- #2 is already closed; no further closure action needed.
- #3 stays open: parsing is merged, and `sample_data.py` composes the parser with
  persistence, but a successful live parse → retrieval run was not verified here.
- #5 stays open: foundation exists on branch, with no PR in the audited list.
- #7 stays open until the working session, card review and prototype checkpoint
  are confirmed. Documentation readiness alone does not prove coordination happened.
- #18 stays open until the connected demo passes and engineers confirm status.

## Verification performed

- `python -m unittest backend.app.services.recommendations.test_engine -v`: 16 passed.
- `python -m backend.app.services.recommendations.demo`: all eight synthetic scenarios passed.
- `python 'backend/Maddie/Week 1/NoteReqDraft.py'`: ten notes loaded, zero sample
  errors; empty/binary/missing-ID examples rejected as expected.
- Source/branch comparison: router registration, contracts, fixture availability,
  frontend types, issue states and merged PRs inspected.
- Database/API/frontend runtime checks not run: this workspace lacks SQLAlchemy
  and no local PostgreSQL setup was established. PR #22's Recall@5=1.00 and PR
  #20's test report are author-reported evidence, not new results from this audit.

## Confirmation record (pending)

Each owner should supply: `done / partial / blocked`, PR/commit, command and actual
result, remaining work, next step, and acknowledgment of consumed contract changes.
Do not fill in acknowledgments on their behalf.
