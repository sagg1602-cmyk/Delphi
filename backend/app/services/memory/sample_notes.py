"""Placeholder sample notes until Maddie's dataset is in. Fictional."""

SAMPLE_NOTES = [
    {
        "id": 1,
        "user_id": 1,
        "title": "Photosynthesis Lecture Notes",
        "content": (
            "Photosynthesis turns light energy into chemical energy. "
            "The light reactions happen in the thylakoid membrane and make ATP. "
            "The Calvin cycle uses ATP to fix carbon dioxide into sugar."
        ),
        "source_type": "markdown",
    },
    {
        "id": 2,
        "user_id": 1,
        "title": "Linear Algebra: Eigenvalues",
        "content": (
            "An eigenvector of a matrix only gets stretched, not rotated. "
            "The eigenvalue is the stretch factor. Find them by solving "
            "det(A - lambda I) = 0."
        ),
        "source_type": "markdown",
    },
    {
        "id": 3,
        "user_id": 1,
        "title": "History Paper Outline",
        "content": (
            "Paper topic: causes of the French Revolution. "
            "Intro, three body paragraphs on debt, inequality and Enlightenment ideas. "
            "Draft due Friday."
        ),
        "source_type": "manual",
    },
    {
        "id": 4,
        "user_id": 1,
        "title": "Memory and Learning (Psych 51)",
        "content": (
            "Spaced repetition beats cramming. Retrieval practice, like quizzing "
            "yourself, makes memories stronger than rereading notes."
        ),
        "source_type": "markdown",
    },
    {
        "id": 5,
        "user_id": 1,
        "title": "Python Study Plan",
        "content": (
            "Practice lists, dictionaries and loops. Do two LeetCode problems a week. "
            "Review recursion before the CS midterm."
        ),
        "source_type": "manual",
    },
    {
        # user 2, should never show up for user 1
        "id": 6,
        "user_id": 2,
        "title": "Photosynthesis Quiz Review",
        "content": "Sam's private notes on chloroplasts and the Calvin cycle.",
        "source_type": "markdown",
    },
]
