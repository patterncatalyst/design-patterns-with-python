"""Shortcut patterns: a table lookup inside the try, an EAFP duty-rate read."""

from generate_diagram import emit

emit(
    "31-shortcut-patterns-dict-dispatch-and-eafp",
    1220,
    480,
    nodes=[
        {
            "x": 30,
            "y": 30,
            "w": 340,
            "h": 50,
            "style": "user",
            "lines": ["issue(kind, consignment_id)"],
        },
        {
            "x": 30,
            "y": 140,
            "w": 340,
            "h": 80,
            "style": "accent",
            "lines": [
                "issuers[kind]",
                "one lookup inside the try",
                "KeyError becomes UnsupportedDocumentError",
            ],
        },
        {
            "x": 410,
            "y": 145,
            "w": 230,
            "h": 70,
            "style": "box",
            "lines": [
                "ISSUERS",
                "frozendict, read-only",
                "a test walks every DocumentKind",
            ],
        },
        {
            "x": 30,
            "y": 280,
            "w": 340,
            "h": 60,
            "style": "box",
            "lines": ["issuer(consignment_id)", "outside the try: its own errors pass through"],
        },
        {
            "x": 30,
            "y": 400,
            "w": 340,
            "h": 50,
            "style": "box",
            "lines": ["reference"],
        },
        {
            "x": 700,
            "y": 30,
            "w": 470,
            "h": 50,
            "style": "user",
            "lines": ["DutyRateCache.rate_for(hs_code)"],
        },
        {
            "x": 680,
            "y": 150,
            "w": 250,
            "h": 80,
            "style": "ghost",
            "lines": ["look first: in, then read", "an eviction in the gap", "raises KeyError"],
        },
        {
            "x": 950,
            "y": 150,
            "w": 220,
            "h": 80,
            "style": "accent",
            "lines": ["ask forgiveness: read once", "on KeyError, load", "and store the rate"],
        },
    ],
    edges=[
        {"x1": 200, "y1": 80, "x2": 200, "y2": 140},
        {"x1": 410, "y1": 180, "x2": 370, "y2": 180},
        {"x1": 200, "y1": 220, "x2": 200, "y2": 280},
        {"x1": 200, "y1": 340, "x2": 200, "y2": 400},
        {"x1": 805, "y1": 80, "x2": 805, "y2": 150},
        {"x1": 1060, "y1": 80, "x2": 1060, "y2": 150},
    ],
)
