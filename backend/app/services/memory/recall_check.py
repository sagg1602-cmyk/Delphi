"""Recall@5 over Maddie's sample notes. Run from backend/: python -m app.services.memory.recall_check"""

from sqlalchemy import text

from app.core.database import init_schema, make_engine
from app.services.memory.retrieval import build_task_query, retrieve_notes
from app.services.memory.sample_data import insert_sample_notes, test_database_url

CHECK_USER_ID = 9001

# (query, expected Maddie note IDs)
SCENARIOS = [
    ("Calvin cycle and chloroplasts", {1}),
    ("Econ problem set on equilibrium price", {2}),
    (build_task_query("Practice sorted list algorithms", ["computer science"]), {3}),
    ("History essay on the Bastille and Napoleon", {4}),
    ("Physics quiz: force, mass and acceleration", {5}),
    ("Biology exam: cell division phases", {6}),
    (build_task_query("Stats homework on residuals", ["data science"]), {7}),
    ("English paper on revenge and madness", {8}),
    ("Chemistry: electronegativity across a period", {9}),
    ("Earthquakes and volcanoes at plate boundaries", {10}),
]


def recall_at_5(db, user_id, id_map):
    db_to_maddie = {db_id: m_id for m_id, db_id in id_map.items()}
    total = 0.0
    lines = []
    for query, expected in SCENARIOS:
        results = retrieve_notes(db, user_id, query, limit=5)
        found = {db_to_maddie[r["note_id"]] for r in results}
        recall = len(found & expected) / len(expected)
        total += recall
        lines.append(f"  {recall:.2f}  {query!r} expected {sorted(expected)} got {sorted(found)}")
    return total / len(SCENARIOS), lines


def main():
    engine = make_engine(test_database_url())
    init_schema(engine)
    with engine.connect() as db:
        tx = db.begin()
        try:
            db.execute(
                text("INSERT INTO users (id, name) VALUES (:id, 'recall check') "
                     "ON CONFLICT (id) DO NOTHING"),
                {"id": CHECK_USER_ID},
            )
            id_map = insert_sample_notes(db, CHECK_USER_ID)
            score, lines = recall_at_5(db, CHECK_USER_ID, id_map)
        finally:
            tx.rollback()
    engine.dispose()
    print("\n".join(lines))
    print(f"\nRecall@5 over {len(SCENARIOS)} scenarios: {score:.2f}")


if __name__ == "__main__":
    main()
