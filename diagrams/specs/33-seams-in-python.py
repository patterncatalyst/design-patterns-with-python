"""Seams in Python: a patch lands in the namespace where the engine looks the name up."""

from generate_diagram import emit

emit(
    "33-seams-in-python",
    1020,
    610,
    nodes=[
        {
            "x": 40,
            "y": 30,
            "w": 440,
            "h": 60,
            "style": "user",
            "lines": ["test", 'monkeypatch.setattr("seams.legacy.request_quote", fake)'],
        },
        {
            "x": 40,
            "y": 150,
            "w": 440,
            "h": 80,
            "style": "accent",
            "lines": [
                "namespace of seams.legacy",
                "request_quote, airco, MARGIN, RateEngine",
            ],
        },
        {
            "x": 40,
            "y": 380,
            "w": 440,
            "h": 70,
            "style": "box",
            "lines": [
                "RateEngine",
                "quote looks the names up; __init__ holds the margin default",
            ],
        },
        {
            "x": 560,
            "y": 145,
            "w": 400,
            "h": 90,
            "style": "ghost",
            "lines": [
                "patch on seams.fastline.request_quote",
                "no effect on RateEngine.quote:",
                "seams.legacy holds its own name",
            ],
        },
        {
            "x": 560,
            "y": 375,
            "w": 400,
            "h": 80,
            "style": "ghost",
            "lines": [
                "margin=MARGIN in __init__",
                "read when the class was defined;",
                "a later patch of MARGIN misses it",
            ],
        },
        {
            "x": 40,
            "y": 520,
            "w": 920,
            "h": 50,
            "style": "ink",
            "lines": ["mypy checks neither the target string nor the replacement"],
        },
    ],
    edges=[
        {"x1": 260, "y1": 90, "x2": 260, "y2": 150},
        {
            "x1": 90,
            "y1": 230,
            "x2": 90,
            "y2": 380,
            "label": "request_quote: looked up in seams.legacy",
            "lx": 150,
            "ly": -40,
        },
        {
            "x1": 430,
            "y1": 230,
            "x2": 430,
            "y2": 380,
            "label": "airco.price: looked up on seams.airco",
            "lx": -110,
            "ly": 25,
        },
        {"x1": 560, "y1": 190, "x2": 480, "y2": 190, "dashed": True},
        {"x1": 560, "y1": 415, "x2": 480, "y2": 415, "dashed": True},
    ],
)
