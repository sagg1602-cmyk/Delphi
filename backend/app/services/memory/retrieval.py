"""Week 1 note retrieval with keyword matching.

Searches an in-memory list of notes. Week 2 moves this onto
PostgreSQL full-text search with the same output format.
"""

import re

from app.services.memory.sample_notes import SAMPLE_NOTES

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "i", "in", "is", "it", "my", "of", "on", "or", "the", "to", "what",
    "with", "about", "do", "does", "me", "notes", "note",
}

TITLE_WEIGHT = 2
CONTENT_WEIGHT = 1
EXCERPT_LENGTH = 120


def tokenize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def make_excerpt(content, query_words):
    lower = content.lower()
    positions = [lower.find(w) for w in query_words if lower.find(w) != -1]
    start = max(min(positions) - 30, 0) if positions else 0
    if start > 0:
        next_space = content.find(" ", start)
        start = next_space + 1 if next_space != -1 else start
    snippet = content[start:start + EXCERPT_LENGTH].strip()
    if start > 0:
        snippet = "..." + snippet
    if start + EXCERPT_LENGTH < len(content):
        snippet += "..."
    return snippet


def score_note(note, query_words):
    title_words = set(tokenize(note["title"]))
    content_words = set(tokenize(note["content"]))
    score = 0
    for word in query_words:
        if word in title_words:
            score += TITLE_WEIGHT
        if word in content_words:
            score += CONTENT_WEIGHT
    return score


def retrieve_notes(user_id, query, limit=5, notes=None):
    """Return the user's best matching notes, best first.

    Each result has note_id, title, excerpt, score (0 to 1), and source_type.
    Returns [] when nothing matches.
    """
    if notes is None:
        notes = SAMPLE_NOTES

    query_words = list(dict.fromkeys(tokenize(query)))
    if not query_words:
        return []

    max_score = len(query_words) * (TITLE_WEIGHT + CONTENT_WEIGHT)
    results = []
    for note in notes:
        if note["user_id"] != user_id:
            continue
        raw = score_note(note, query_words)
        if raw == 0:
            continue
        results.append({
            "note_id": note["id"],
            "title": note["title"],
            "excerpt": make_excerpt(note["content"], query_words),
            "score": round(raw / max_score, 2),
            "source_type": note["source_type"],
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:limit]
