"""Week 1 demo. Run from backend/: python -m app.services.memory.demo"""

from app.services.memory.retrieval import retrieve_notes

DEMO_QUERIES = [
    "calvin cycle",
    "eigenvalues matrix",
    "how do I study for my midterm",
    "french revolution paper",
    "quantum physics",
]


def main():
    for query in DEMO_QUERIES:
        print(f'\nQuery: "{query}"')
        results = retrieve_notes(1, query, limit=3)
        if not results:
            print("  (no matching notes)")
        for r in results:
            print(f'  [{r["score"]:.2f}] note {r["note_id"]}  {r["title"]}')
            print(f'         {r["excerpt"]}')


if __name__ == "__main__":
    main()
