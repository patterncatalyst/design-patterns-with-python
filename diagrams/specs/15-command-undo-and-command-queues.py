"""Amendments as values: a first-in first-out queue, apply, and bounded undo and redo stacks."""

from generate_diagram import emit

MAIN_X = 340
MAIN_W = 300
MID = MAIN_X + MAIN_W // 2

emit(
    "15-command-undo-and-command-queues",
    990,
    715,
    nodes=[
        {
            "x": MAIN_X,
            "y": 30,
            "w": MAIN_W,
            "h": 56,
            "style": "accent",
            "lines": ["submit(amendment)"],
        },
        {
            "x": MAIN_X,
            "y": 140,
            "w": MAIN_W,
            "h": 56,
            "style": "box",
            "lines": ["pending", "deque, first in first out"],
        },
        {
            "x": MAIN_X,
            "y": 250,
            "w": MAIN_W,
            "h": 70,
            "style": "ink",
            "lines": ["apply_pending", "fold on a local request:", "all or nothing"],
        },
        {
            "x": MAIN_X,
            "y": 370,
            "w": MAIN_W,
            "h": 56,
            "style": "user",
            "lines": ["apply(request, amendment)", "one match, one function"],
        },
        {
            "x": 60,
            "y": 490,
            "w": 240,
            "h": 56,
            "style": "box",
            "lines": ["BookingRequest", "new frozen value"],
        },
        {
            "x": 440,
            "y": 490,
            "w": 240,
            "h": 56,
            "style": "box",
            "lines": ["inverse amendment", "read at the moment of change"],
        },
        {
            "x": 440,
            "y": 630,
            "w": 240,
            "h": 56,
            "style": "accent",
            "lines": ["undo_stack", "deque(maxlen): oldest forgotten"],
        },
        {
            "x": 780,
            "y": 630,
            "w": 190,
            "h": 56,
            "style": "box",
            "lines": ["redo_stack", "deque"],
        },
        {
            "x": 780,
            "y": 490,
            "w": 190,
            "h": 56,
            "style": "ghost",
            "lines": ["new amendment", "clears redo"],
        },
    ],
    edges=[
        {"x1": MID, "y1": 86, "x2": MID, "y2": 140},
        {"x1": MID, "y1": 196, "x2": MID, "y2": 250},
        {"x1": MID, "y1": 320, "x2": MID, "y2": 370},
        {"x1": 420, "y1": 426, "x2": 180, "y2": 490},
        {"x1": 560, "y1": 426, "x2": 560, "y2": 490},
        {"x1": 560, "y1": 546, "x2": 560, "y2": 630},
        {"x1": 680, "y1": 645, "x2": 780, "y2": 645, "label": "undo"},
        {"x1": 780, "y1": 672, "x2": 680, "y2": 672, "label": "redo"},
        {"x1": 875, "y1": 546, "x2": 875, "y2": 630, "dashed": True},
    ],
)
