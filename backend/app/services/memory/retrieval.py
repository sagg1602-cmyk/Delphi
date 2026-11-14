"""Note retrieval with PostgreSQL full-text search.

Searches the notes table. Title words rank above content words, and any
query word can match (OR), so long task titles still find notes.
"""

import re

from sqlalchemy import text
from sqlalchemy.engine import Connection

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "i", "in", "into", "is", "it", "my", "of", "on", "or", "the", "to",
    "what", "with", "about", "do", "does", "me", "notes", "note", "this",
    "that",
}

EXCERPT_LENGTH = 160

# ts_rank has no upper limit. Normalization option 32 divides rank by
# (rank + 1), so scores stay between 0 and 1.
SEARCH_SQL = text(
    """
    WITH q AS (SELECT to_tsquery('english', :tsquery) AS query)
    SELECT n.id, n.user_id, n.title, n.content, n.source_type,
           ts_rank(
               setweight(to_tsvector('english', n.title), 'A')
               || setweight(to_tsvector('english', n.content), 'B'),
               q.query,
               32
           ) AS score
    FROM notes n, q
    WHERE n.user_id = :user_id
      AND (
          setweight(to_tsvector('english', n.title), 'A')
          || setweight(to_tsvector('english', n.content), 'B')
      ) @@ q.query
    ORDER BY score DESC, n.id
    LIMIT :limit
    """
)


def query_words(query):
    words = re.findall(r"[a-z0-9]+", query.lower())
    return list(dict.fromkeys(w for w in words if w not in STOPWORDS))


def make_excerpt(content, words):
    lower = content.lower()
    hits = [lower.find(w) for w in words if lower.find(w) != -1]
    start = max(min(hits) - 40, 0) if hits else 0
    if start > 0:
        next_space = content.find(" ", start)
        start = next_space + 1 if next_space != -1 else start
    snippet = " ".join(content[start:start + EXCERPT_LENGTH].split())
    if start > 0:
        snippet = "..." + snippet
    if start + EXCERPT_LENGTH < len(content):
        snippet += "..."
    return snippet


def retrieve_notes(db: Connection, user_id: int, query: str, limit: int = 5) -> list[dict]:
    """Return the user's best matching notes, best first.

    Each result has note_id, user_id, title, excerpt, score (0 to 1),
    and source_type. Returns [] when nothing matches.
    """
    words = query_words(query)
    if not words or limit <= 0:
        return []

    rows = db.execute(
        SEARCH_SQL,
        {"tsquery": " | ".join(words), "user_id": user_id, "limit": limit},
    ).mappings().all()

    return [
        {
            "note_id": row["id"],
            "user_id": row["user_id"],
            "title": row["title"],
            "excerpt": make_excerpt(row["content"], words),
            "score": round(float(row["score"]), 3),
            "source_type": row["source_type"],
        }
        for row in rows
    ]


def build_task_query(task_title, interests=()):
    """Turn a task title and active interests into a search string.

    build_task_query("Draft research introduction",
                     [{"name": "cognition", "active": True},
                      {"name": "chess", "active": False}])
    -> "draft research introduction cognition"
    """
    names = []
    for interest in interests:
        if isinstance(interest, str):
            names.append(interest)
        elif interest.get("active", True):
            names.append(interest.get("name", ""))
    return " ".join(query_words(" ".join([task_title or ""] + names)))
