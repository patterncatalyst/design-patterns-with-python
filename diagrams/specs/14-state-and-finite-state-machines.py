"""Consignment lifecycle two ways: a read-only table and a match over frozen states."""

from itertools import pairwise

from generate_diagram import emit

COL_X = 330
COL_W = 240
COL_H = 56
CENTER = COL_X + COL_W // 2
STATE_Y = [40, 160, 280, 400, 520]
STATES = [
    ("Booked", None),
    ("Loaded", None),
    ("InTransit", None),
    ("Cleared", None),
    ("Delivered", "terminal"),
]
EVENTS = ["LOADED", "DEPARTED", "CLEARED", "DELIVERED"]

nodes = [
    {
        "x": 20,
        "y": 30,
        "w": 270,
        "h": 76,
        "style": "box",
        "lines": ["TRANSITIONS", "read-only table:", "status, event to status"],
    },
    {
        "x": 610,
        "y": 30,
        "w": 270,
        "h": 76,
        "style": "box",
        "lines": ["apply_event", "match on state,", "assert_never"],
    },
    {
        "x": 610,
        "y": 270,
        "w": 270,
        "h": 76,
        "style": "ghost",
        "lines": ["each day: delay with", "probability p", "(injected Random)"],
    },
    {
        "x": COL_X,
        "y": 650,
        "w": COL_W,
        "h": 70,
        "style": "accent",
        "lines": ["illegal event:", "TransitionError"],
    },
]
for (name, note), y in zip(STATES, STATE_Y, strict=True):
    lines = [name] if note is None else [name, note]
    style = "ink" if note else "user"
    nodes.append(
        {
            "x": COL_X,
            "y": y,
            "w": COL_W,
            "h": COL_H + (14 if note else 0),
            "style": style,
            "lines": lines,
        }
    )

edges = [
    {"x1": 290, "y1": 68, "x2": COL_X, "y2": 68, "dashed": True},
    {"x1": 610, "y1": 68, "x2": COL_X + COL_W, "y2": 68, "dashed": True},
    {"x1": 610, "y1": 308, "x2": COL_X + COL_W, "y2": 308, "dashed": True},
    {"x1": CENTER, "y1": 590, "x2": CENTER, "y2": 650, "dashed": True, "label": "any other event"},
]
for (a, b), kind in zip(pairwise(STATE_Y), EVENTS, strict=True):
    edges.append({"x1": CENTER, "y1": a + COL_H, "x2": CENTER, "y2": b, "label": kind})

emit("14-state-and-finite-state-machines", 900, 740, nodes=nodes, edges=edges)
