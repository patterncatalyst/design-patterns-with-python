"""One quote, three rules in a slot: the registry returns a callable and quote records its name."""

from generate_diagram import emit

RULE_Y = 260
RULE_W = 250

emit(
    "12-strategy-the-callable",
    820,
    540,
    nodes=[
        {
            "x": 230,
            "y": 30,
            "w": 360,
            "h": 56,
            "style": "accent",
            "lines": ['quote(consignment, "zone")', "the caller names a rule"],
        },
        {
            "x": 230,
            "y": 140,
            "w": 360,
            "h": 56,
            "style": "ink",
            "lines": ["RATE_RULES", "read-only, selected by name"],
        },
        {
            "x": 640,
            "y": 140,
            "w": 160,
            "h": 56,
            "style": "box",
            "lines": ["unknown name", "RatingError"],
        },
        {
            "x": 20,
            "y": RULE_Y,
            "w": RULE_W,
            "h": 66,
            "style": "box",
            "lines": ["flat_rate", "function"],
        },
        {
            "x": 285,
            "y": RULE_Y,
            "w": RULE_W,
            "h": 66,
            "style": "box",
            "lines": ["partial(per_kg, rate=...)", "bound configuration"],
        },
        {
            "x": 550,
            "y": RULE_Y,
            "w": RULE_W,
            "h": 66,
            "style": "box",
            "lines": ["ZoneRate(TARIFF)", "rule object: equal, hashable"],
        },
        {
            "x": 230,
            "y": 430,
            "w": 360,
            "h": 56,
            "style": "accent",
            "lines": ["RateQuote", "records rule name and price"],
        },
    ],
    edges=[
        {"x1": 410, "y1": 86, "x2": 410, "y2": 140},
        {"x1": 590, "y1": 168, "x2": 640, "y2": 168},
        {"x1": 410, "y1": 196, "x2": 145, "y2": RULE_Y},
        {"x1": 410, "y1": 196, "x2": 410, "y2": RULE_Y},
        {"x1": 410, "y1": 196, "x2": 675, "y2": RULE_Y},
        {"x1": 145, "y1": RULE_Y + 66, "x2": 330, "y2": 430},
        {"x1": 410, "y1": RULE_Y + 66, "x2": 410, "y2": 430},
        {"x1": 675, "y1": RULE_Y + 66, "x2": 490, "y2": 430},
    ],
)
