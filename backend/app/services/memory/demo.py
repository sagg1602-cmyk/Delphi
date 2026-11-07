"""Week 2 demo. Run from backend/: python -m app.services.memory.demo"""

from sqlalchemy import text

from app.core.database import init_schema, make_engine
from app.services.memory.recall_check import SCENARIOS, recall_at_5
from app.services.memory.retrieval import build_task_query, retrieve_notes
from app.services.memory.sample_data import insert_sample_notes, test_database_url

ALEX, SAM = 9101, 9102


def show(db, user_id, query, label):
    print(f'\n{label}\n  query: "{query}"')
    results = retrieve_notes(db, user_id, query, limit=3)
    if not results:
        print("  (no matching notes)")
    for r in results:
        print(f'  [{r["score"]:.3f}] note {r["note_id"]}  {r["title"]}')
        print(f'          {r["excerpt"]}')
    return results


def main():
    engine = make_engine(test_database_url())
    init_schema(engine)
    with engine.connect() as db:
        tx = db.begin()
        try:
            db.execute(text("INSERT INTO users (id, name) VALUES (:a, 'demo alex'), "
                            "(:s, 'demo sam') ON CONFLICT (id) DO NOTHING"),
                       {"a": ALEX, "s": SAM})
            id_map = insert_sample_notes(db, ALEX)
            print(f"Loaded {len(id_map)} of Maddie's sample notes for Alex.")

            show(db, ALEX, build_task_query("Bio exam on cell division", ["biology"]),
                 "1) Task: 'Bio exam on cell division' + interest 'biology'")
            show(db, ALEX, build_task_query("Draft econ essay", ["price trends"]),
                 "2) Task: 'Draft econ essay' + interest 'price trends'")
            first = show(db, ALEX, "earthquakes and volcanoes",
                         "3) Interest search: earthquakes and volcanoes")

            score, lines = recall_at_5(db, ALEX, id_map)
            print("\n4) Retrieval check (before any deletes)")
            print("\n".join(lines))
            print(f"  Recall@5 over {len(SCENARIOS)} scenarios: {score:.2f}")

            gone = first[0]["note_id"]
            db.execute(text("DELETE FROM notes WHERE id = :id"), {"id": gone})
            show(db, ALEX, "earthquakes and volcanoes", f"5) After deleting note {gone}")

            show(db, SAM, "photosynthesis cells force", "6) Second user Sam, same kind of search")

        finally:
            tx.rollback()
    engine.dispose()


if __name__ == "__main__":
    main()
