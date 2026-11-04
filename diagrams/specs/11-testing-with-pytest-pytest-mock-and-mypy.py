"""How a claim becomes evidence: a witness test, seen failing, then a fresh quoted run."""

from generate_diagram import emit

emit(
    "11-testing-with-pytest-pytest-mock-and-mypy",
    840,
    470,
    nodes=[
        {
            "x": 60,
            "y": 30,
            "w": 400,
            "h": 56,
            "style": "accent",
            "lines": ["claim", "the engine books only the winner"],
        },
        {
            "x": 60,
            "y": 140,
            "w": 400,
            "h": 56,
            "style": "box",
            "lines": ["witness test", "test_book_best_books_only_the_winner"],
        },
        {
            "x": 60,
            "y": 250,
            "w": 400,
            "h": 56,
            "style": "box",
            "lines": ["seen failing", "deletion in a scratch copy"],
        },
        {
            "x": 60,
            "y": 360,
            "w": 400,
            "h": 56,
            "style": "ink",
            "lines": ["quoted output", "fresh, scrubbed run"],
        },
        {
            "x": 530,
            "y": 140,
            "w": 280,
            "h": 56,
            "style": "user",
            "lines": ["negative fixture", "shows the failure the claim rules out"],
        },
    ],
    edges=[
        {"x1": 260, "y1": 86, "x2": 260, "y2": 140},
        {"x1": 260, "y1": 196, "x2": 260, "y2": 250},
        {"x1": 260, "y1": 306, "x2": 260, "y2": 360},
        {"x1": 530, "y1": 168, "x2": 460, "y2": 168},
    ],
)
