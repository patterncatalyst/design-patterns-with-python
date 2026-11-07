"""Refactor or rewrite: a router splits zones between two engines and a parity table holds them."""

from generate_diagram import emit

emit(
    "36-refactor-or-rewrite",
    1160,
    640,
    nodes=[
        {
            "x": 250,
            "y": 30,
            "w": 300,
            "h": 60,
            "style": "box",
            "lines": ["Consignment", "zone and weight"],
        },
        {
            "x": 40,
            "y": 150,
            "w": 720,
            "h": 80,
            "style": "accent",
            "lines": ["Router", "zone in migrated?"],
        },
        {
            "x": 40,
            "y": 330,
            "w": 340,
            "h": 80,
            "style": "box",
            "lines": ["rating.quote", "Tariff; bisect_left keeps limits inclusive"],
        },
        {
            "x": 420,
            "y": 330,
            "w": 340,
            "h": 80,
            "style": "box",
            "lines": ["legacy.RateEngine.quote", "served"],
        },
        {
            "x": 840,
            "y": 325,
            "w": 280,
            "h": 90,
            "style": "ghost",
            "lines": [
                "rewrite in shadow",
                "when report is set:",
                "compared, never served;",
                "Mismatch on a difference",
            ],
        },
        {
            "x": 40,
            "y": 520,
            "w": 720,
            "h": 70,
            "style": "ink",
            "lines": ["parity table", "the rows that differ must equal ACCEPTED_DIFFERENCES"],
        },
        {
            "x": 840,
            "y": 520,
            "w": 280,
            "h": 70,
            "style": "ghost",
            "lines": ["first draft with bisect_right", "differs at the band limits"],
        },
    ],
    edges=[
        {"x1": 400, "y1": 90, "x2": 400, "y2": 150},
        {"x1": 210, "y1": 230, "x2": 210, "y2": 330, "label": "yes", "lx": 20},
        {"x1": 590, "y1": 230, "x2": 590, "y2": 330, "label": "no", "lx": 20},
        {"x1": 760, "y1": 370, "x2": 840, "y2": 370, "dashed": True},
        {"x1": 210, "y1": 410, "x2": 210, "y2": 520},
        {"x1": 590, "y1": 410, "x2": 590, "y2": 520},
        {"x1": 840, "y1": 555, "x2": 760, "y2": 555, "dashed": True},
    ],
)
