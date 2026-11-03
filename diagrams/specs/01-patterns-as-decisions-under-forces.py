"""The rate-quote decision under four forces."""

from generate_diagram import emit

FX = [30, 225, 420, 615]
FW = 175

forces = [
    ("Carrier tariffs", "zone and weight bands"),
    ("Surcharges, discounts", "commercial, set per contract"),
    ("Destination tax", "varies by country"),
    ("Reproducible quotes", "billing disputes replay them"),
]

emit(
    "01-patterns-as-decisions-under-forces",
    820,
    620,
    bands=[{"x": 15, "y": 130, "w": 790, "h": 110, "label": "Forces pulling on the design"}],
    nodes=[
        {
            "x": 230,
            "y": 20,
            "w": 360,
            "h": 56,
            "style": "box",
            "lines": ["Problem: quote a consignment", "one rate per carrier, zone and weight"],
        },
        *[
            {
                "x": FX[i],
                "y": 165,
                "w": FW,
                "h": 56,
                "style": "box",
                "lines": [t, d],
            }
            for i, (t, d) in enumerate(forces)
        ],
        {
            "x": 230,
            "y": 300,
            "w": 360,
            "h": 56,
            "style": "accent",
            "lines": [
                "Decision: where the rating rules live",
                "the rule that best resolves the forces",
            ],
        },
        {
            "x": 230,
            "y": 400,
            "w": 360,
            "h": 56,
            "style": "box",
            "lines": ["Consequences", "what the choice buys and what it costs"],
        },
        {
            "x": 230,
            "y": 500,
            "w": 360,
            "h": 56,
            "style": "ink",
            "lines": [
                "The shape follows the dominant force",
                "one function, separate callables, or a Protocol",
            ],
        },
    ],
    edges=[
        {"x1": 410, "y1": 76, "x2": 410, "y2": 130},
        *[{"x1": FX[i] + FW / 2, "y1": 221, "x2": 330 + i * 53.3, "y2": 300} for i in range(4)],
        {"x1": 410, "y1": 356, "x2": 410, "y2": 400},
        {"x1": 410, "y1": 456, "x2": 410, "y2": 500},
    ],
)
