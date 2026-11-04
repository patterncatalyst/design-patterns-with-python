"""One dataclass declaration writes the Value Object's structure for SlotId."""

from generate_diagram import emit

CELLS = [
    ["__init__", "the constructor"],
    ["__repr__", "readable text"],
    ["__eq__ and __hash__", "compare by content"],
    ["__lt__ to __ge__", "from order=True"],
    ["__setattr__", "FrozenInstanceError"],
    ["__slots__", "no per-instance dict"],
]
W = 170
GAP = 16
MARGIN = 20
CANVAS = 2 * MARGIN + len(CELLS) * W + (len(CELLS) - 1) * GAP
MID = CANVAS // 2

nodes = [
    {
        "x": MID - 280,
        "y": 30,
        "w": 560,
        "h": 56,
        "style": "accent",
        "lines": [
            "@dataclass(frozen=True, slots=True, order=True)",
            "class SlotId: bay, row, tier",
        ],
    },
    {
        "x": MID - 280,
        "y": 330,
        "w": 560,
        "h": 56,
        "style": "ink",
        "lines": [
            "Value Object force",
            "compared by content, safe to share, usable as a key",
        ],
    },
    {
        "x": MID - 280,
        "y": 440,
        "w": 560,
        "h": 90,
        "style": "user",
        "lines": [
            "Left to you",
            "the invariant in __post_init__",
            "immutable field types",
            "value or entity",
        ],
    },
]
edges = []
for i, lines in enumerate(CELLS):
    x = MARGIN + i * (W + GAP)
    nodes.append({"x": x, "y": 180, "w": W, "h": 56, "style": "box", "lines": lines})
    cx = x + W // 2
    edges.append({"x1": MID, "y1": 86, "x2": cx, "y2": 180})
    edges.append({"x1": cx, "y1": 236, "x2": MID - 200 + i * 80, "y2": 330})

emit("08-dataclasses-and-value-semantics", CANVAS, 560, nodes=nodes, edges=edges)
