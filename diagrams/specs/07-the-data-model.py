"""factor * price: the left operand asks first, then the reflected method answers."""

from generate_diagram import emit

emit(
    "07-the-data-model",
    820,
    560,
    nodes=[
        {
            "x": 230,
            "y": 30,
            "w": 360,
            "h": 56,
            "style": "accent",
            "lines": ["factor * price", "the expression the interpreter evaluates"],
        },
        {
            "x": 230,
            "y": 140,
            "w": 360,
            "h": 56,
            "style": "box",
            "lines": ["Decimal.__mul__(factor, price)", "left operand's type asks first"],
        },
        {
            "x": 230,
            "y": 250,
            "w": 360,
            "h": 56,
            "style": "box",
            "lines": ["Money.__rmul__(price, factor)", "reflected method answers"],
        },
        {
            "x": 230,
            "y": 360,
            "w": 360,
            "h": 56,
            "style": "ink",
            "lines": ["Money", "the result"],
        },
        {
            "x": 500,
            "y": 470,
            "w": 300,
            "h": 56,
            "style": "accent",
            "lines": ["TypeError", "only when both decline"],
        },
    ],
    edges=[
        {"x1": 410, "y1": 86, "x2": 410, "y2": 140},
        {
            "x1": 410,
            "y1": 196,
            "x2": 410,
            "y2": 250,
            "label": "NotImplemented",
            "lx": 80,
            "ly": 0,
        },
        {"x1": 410, "y1": 306, "x2": 410, "y2": 360, "label": "returns", "lx": 50, "ly": 0},
        {
            "x1": 590,
            "y1": 292,
            "x2": 650,
            "y2": 470,
            "dashed": True,
            "label": "NotImplemented again",
            "lx": 100,
            "ly": 0,
        },
    ],
)
