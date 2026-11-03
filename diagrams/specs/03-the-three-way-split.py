"""Two questions sort every catalogue pattern into three bands."""

from generate_diagram import emit

BX, BW = 420, 380


def lines(x, y0, items):
    return [
        {"x": x, "y": y0 + i * 24, "text": t, "size": 12.5, "color": "#111111"}
        for i, t in enumerate(items)
    ]


emit(
    "03-the-three-way-split",
    820,
    620,
    bands=[
        {"x": BX, "y": 20, "w": BW, "h": 150, "label": "Needs disambiguating"},
        {"x": BX, "y": 190, "w": BW, "h": 250, "label": "Dissolves into a language feature"},
        {"x": BX, "y": 460, "w": BW, "h": 140, "label": "Survives with its shape"},
    ],
    nodes=[
        {
            "x": 20,
            "y": 62,
            "w": 340,
            "h": 66,
            "style": "box",
            "lines": ["Does the name mean two things", "in Python?"],
        },
        {
            "x": 20,
            "y": 282,
            "w": 340,
            "h": 66,
            "style": "accent",
            "lines": ["Does a language feature", "remove the force?"],
        },
        {
            "x": 20,
            "y": 497,
            "w": 340,
            "h": 56,
            "style": "ink",
            "lines": ["The force remains", "so the structure stays"],
        },
    ],
    edges=[
        {"x1": 360, "y1": 95, "x2": BX, "y2": 95, "label": "yes", "lx": 0, "ly": -8},
        {"x1": 190, "y1": 128, "x2": 190, "y2": 282, "label": "no", "lx": 16, "ly": 0},
        {"x1": 360, "y1": 315, "x2": BX, "y2": 315, "label": "yes", "lx": 0, "ly": -8},
        {"x1": 190, "y1": 348, "x2": 190, "y2": 497, "label": "no", "lx": 16, "ly": 0},
        {"x1": 360, "y1": 525, "x2": BX, "y2": 525},
    ],
    notes=[
        *lines(BX + 16, 74, ["Decorator vs @decorator", "Singleton", "Proxy", "Protocol vs ABC"]),
        *lines(
            BX + 16,
            242,
            [
                "Strategy: a callable",
                "Iterator: a generator",
                "Factory Method: a dict of classes",
                "Template Method: hook callables",
                "Builder and Prototype: a dataclass",
                "Visitor: singledispatch or match",
                "Null Object: a type that allows None",
            ],
        ),
        *lines(
            BX + 16,
            512,
            [
                "State and Command with undo",
                "Composite and Observer",
                "Chain of Responsibility and Memento",
            ],
        ),
    ],
)
