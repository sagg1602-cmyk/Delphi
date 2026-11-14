# Delphi — Frontend

Next.js + TypeScript + Tailwind. Talks to the Delphi API through one file: `lib/api-client.ts`.

## Run locally

You need the backend running first (see `backend/HANDOFF.md`). It should answer at http://localhost:8000/health.

```bash
cd frontend
npm install
cp .env.example .env.local   # first time only
npm run dev
```

Open http://localhost:3000. The dot under the sidebar vaults is green when the API is reachable (hover it for details).

### Settings (`frontend/.env.local`)

| Variable | What it does |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | Where the API runs. Default `http://localhost:8000`. |
| `NEXT_PUBLIC_USE_FIXTURES` | `true` = Today shows Youssef's sample (`data/sample_recommendations.json`), labeled **Sample data**. `false` = Today calls the live API. |

Restart `npm run dev` after changing either one.

## Pages

| Route | What it does | API calls |
| --- | --- | --- |
| `/` Today | Knowledge map of today's recommendations. Loading, empty, error-with-retry and refresh. **Why this?** on each card lists its evidence. | `POST /recommendations/generate` |
| `/tasks` | List tasks, add one (title, due date, minutes), tick one complete. | `GET /tasks`, `POST /tasks`, `PATCH /tasks/{id}` |
| `/notes` | List notes, create one (title, content). | `GET /notes`, `POST /notes` |
| `/map`, `/discover` | Placeholders. | none |

## Code map

- `lib/api-client.ts` — base URL, `X-Dev-User: dev-user-1` header, JSON parsing, readable errors. **Every page calls the API only through `api` in this file.**
- `lib/types.ts` — Task, Note, Interest, Recommendation shapes, matching the team contracts.
- `lib/use-api-data.ts` — loads data when a page opens; gives `status`, `data`, `error`, `reload`.
- `components/KnowledgeMap.tsx` — the Today map, its states, and the "Why this?" panel.

## Demo (about 2 minutes)

1. Tasks: add "Calculus problem set" due in two days.
2. Notes: add "Calculus: derivative rules".
3. Today: show the recommendations, open **Why this?** on the study card, show the task and note.
4. Tasks: tick the calculus task complete.
5. Today: press **Refresh**. The calculus recommendation is gone.

## Known gaps (waiting on backend)

- Duration: the API rejects `duration_minutes` until it is added to `TaskCreate`. Tasks without a duration work now.
- `PATCH /tasks/{id}` and `POST /recommendations/generate` must exist on the API for ticking tasks and live Today.
- Recommendations accept either `evidence: [{id, type, label}]` or Week 1 `evidence_ids`. With ids only, the type comes from the prefix (`task_`, `note_`, `interest_`, `resource_`).
