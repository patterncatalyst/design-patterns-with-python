"""Fowler vs Feathers: the same two rounding refactors under intent rows and under golden quotes."""

from generate_diagram import emit

emit(
    "35-fowler-vs-feathers",
    1100,
    660,
    nodes=[
        {
            "x": 620,
            "y": 30,
            "w": 440,
            "h": 70,
            "style": "box",
            "lines": [
                "legacy.RateEngine",
                "carrier functions arrive as keyword parameters",
            ],
        },
        {
            "x": 40,
            "y": 160,
            "w": 440,
            "h": 70,
            "style": "sub",
            "lines": ["INTENT_ROWS", "tests written from the requirement"],
        },
        {
            "x": 620,
            "y": 160,
            "w": 440,
            "h": 70,
            "style": "accent",
            "lines": ["rate_quotes.json", "recorded from the legacy engine"],
        },
        {
            "x": 40,
            "y": 290,
            "w": 1020,
            "h": 80,
            "style": "box",
            "lines": [
                "two rounding refactors of refactored.RateEngine",
                "Replace Primitive with Object: _CentFirstRateEngine",
                "Substitute Algorithm: _RoundBuiltinRateEngine",
            ],
        },
        {
            "x": 40,
            "y": 430,
            "w": 440,
            "h": 70,
            "style": "ghost",
            "lines": ["the intent rows pass both refactors", "no failure names a changed total"],
        },
        {
            "x": 620,
            "y": 430,
            "w": 440,
            "h": 70,
            "style": "box",
            "lines": [
                "the golden quotes list the changed rows",
                "the first row is named in the failure",
            ],
        },
        {
            "x": 40,
            "y": 560,
            "w": 1020,
            "h": 70,
            "style": "ink",
            "lines": [
                "characterise first, then refactor in named steps; run the golden quotes after each"
            ],
        },
    ],
    edges=[
        {"x1": 840, "y1": 100, "x2": 840, "y2": 160},
        {"x1": 260, "y1": 230, "x2": 260, "y2": 290},
        {"x1": 840, "y1": 230, "x2": 840, "y2": 290},
        {"x1": 260, "y1": 370, "x2": 260, "y2": 430},
        {"x1": 840, "y1": 370, "x2": 840, "y2": 430},
        {"x1": 840, "y1": 500, "x2": 840, "y2": 560},
    ],
)
