"""Loading the tariff table once: a ladder to climb in order, and the class forms beside it."""

from generate_diagram import emit

X = 40
W = 440
MID = X + W // 2
SIDE_X = 620
SIDE_W = 300

emit(
    "18-singleton-module-borg-metaclass",
    960,
    680,
    nodes=[
        {
            "x": X,
            "y": 30,
            "w": W,
            "h": 70,
            "style": "user",
            "lines": ["tariff_table", "module: built at import time"],
        },
        {
            "x": X,
            "y": 150,
            "w": W,
            "h": 70,
            "style": "user",
            "lines": ["lazy from ... import tariff_table", "built on first use, once"],
        },
        {
            "x": X,
            "y": 270,
            "w": W,
            "h": 70,
            "style": "box",
            "lines": ["quote(..., table=...)", "passed in: tests and tenants get their own"],
        },
        {
            "x": X,
            "y": 390,
            "w": W,
            "h": 70,
            "style": "ink",
            "lines": ["LoadOnce", "lock with a double check:", "load needs run-time input"],
        },
        {
            "x": SIDE_X,
            "y": 150,
            "w": SIDE_W,
            "h": 70,
            "style": "ghost",
            "lines": ["Borg", "shared state, distinct objects"],
        },
        {
            "x": SIDE_X,
            "y": 270,
            "w": SIDE_W,
            "h": 70,
            "style": "ghost",
            "lines": ["SingletonMeta", "second call's arguments ignored"],
        },
        {
            "x": SIDE_X,
            "y": 390,
            "w": SIDE_W,
            "h": 70,
            "style": "ghost",
            "lines": ["__new__", "reruns __init__"],
        },
        {
            "x": X,
            "y": 540,
            "w": W,
            "h": 70,
            "style": "accent",
            "lines": ["functools.cache memoises;", "it is not call-once"],
        },
    ],
    edges=[
        {"x1": MID, "y1": 100, "x2": MID, "y2": 150},
        {"x1": MID, "y1": 220, "x2": MID, "y2": 270},
        {"x1": MID, "y1": 340, "x2": MID, "y2": 390},
        {"x1": MID, "y1": 460, "x2": MID, "y2": 540, "dashed": True},
    ],
)
