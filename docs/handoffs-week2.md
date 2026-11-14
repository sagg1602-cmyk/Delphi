# Week 2 handoff review

Audit baseline and date: see [mvp-scope.md](mvp-scope.md). Proposed decisions below
need Manny and the consuming engineers' review. No historical Wednesday check-in
or delivery of examples is claimed.

## Contract comparison

| Interface | Observed in main | Required handoff / proposed resolution | Reviewers |
| --- | --- | --- | --- |
| User | `app/core/database.py` always returns integer 1; no header selection | Restore shared dev-user dependency for `X-Dev-User`; keep database IDs integers | Ava, Manny, Youssef, Miya |
| Task | `id`, `user_id`, `title`, `due_date`, `status`, timestamps; GET/POST only | Keep `due_date` (not a second `due_at` field); add Week 2 completion and duration/priority contract | Ava, Youssef, Miya |
| Note request | `title`, `content`, `source_type`; unknown fields rejected | Loader must omit file `id`; add `source_path` only after backend supports it | Ava, Maddie |
| Markdown input | Heading, numeric second-line ID, content | File ID is fixture identity, never the saved database ID; preserve filename separately | Maddie, Xitlaly |
| Retrieved note | `note_id`, `user_id`, `title`, `excerpt`, `score`, `source_type` | Adapter maps `note_id` to engine `id` and supplies searchable text from title/excerpt or stored note; retain user scoping | Xitlaly, Youssef |
| Interests | No interests repository/router/table in main | Restore active-interest repository and agree normalized `id`, `user_id`, `name`, `active` | Ava, Youssef |
| Resource | No `shared/fixtures/resources.json` in main | Catalog fields from #14; actual resource URLs checked by a person; no invented verification | Maddie, Youssef |
| Recommendation | Engine/schema expose `id`, `type`, `title`, `reason`, `estimated_minutes`, `evidence`, `action` | Consume Week 2 fixture; evidence items have `type`, original `id`, `label`; actions are `open_task` or `open_url` with `target` | Youssef, Miya |
| Frontend card | `origin/miya/frontend` types use `evidence_ids` and `action_target` | Replace old fields with Week 2 shape; preserve numeric or string evidence IDs; visible sample-data mode | Miya, Youssef |
| Router/setup | Recommendation router unregistered; sources unconfigured | Register only after real adapter/catalog are ready; missing configuration is an error, not silent fixture fallback | Manny, Ava, Youssef |

Ava's PR #20 describes newer code than main currently contains. Branch
`ava/week2-api` contains the Week 2 API work, but main has retrieval/recommendation
work absent from that branch. Manny should restore it through a focused PR on
current main, preserving later modules; replacing main wholesale would lose work.
Verify code and OpenAPI instead of treating a merged PR description as proof.

## Handoff acceptance checklist

- [ ] Ava + Manny reconcile Week 2 routes, migrations, seed and dev-user dependency on current main.
- [ ] Ava's actual request/response examples reach Miya and Maddie; record acknowledgment or PR link.
- [ ] Maddie posts only accepted NoteCreate fields and keeps a file-ID → database-ID mapping.
- [ ] Xitlaly + Maddie demonstrate parsed note → saved note → retrieval using those database IDs.
- [ ] Youssef adapts retrieval and interests to the normalized context, loads the real catalog, and registers the endpoint.
- [ ] Miya confirms action/evidence fields and merges the frontend through a reviewed PR.
- [ ] Manny runs browser → API → database smoke test; Sebastian records the result and engineer confirmations.

## Working-session agenda (proposed, unscheduled)

Sebastian + Miya (20 minutes): launch the frontend branch, compare its two cards
with `shared/fixtures/recommendations_week2.output.json`, map Why this? labels and
actions, and identify the five required screens/states in #16. Capture decisions
in the PR; the session has not been held or scheduled by this document.

Sebastian + Maddie + Xitlaly (20 minutes): parse Binary Search, preserve its file
identity, save through the accepted API, retrieve its database ID, and agree on the
expanded fixture and ten recall scenarios. Maddie owns parsing/loading and catalog;
Xitlaly owns search/scoring and recall measurement. Manny handles technical conflicts.

Checkpoint: each contributor demonstrates their own component in 3–5 minutes and
states one blocker and next step. Sebastian records evidence; Manny coordinates
review and merge order. Do not claim attendance or confirmations until received.
