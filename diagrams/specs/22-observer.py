"""Observer: what a signal decides about order, failure, re-entry and subscriber lifetime."""

from generate_diagram import emit

emit(
    "22-observer",
    1000,
    720,
    nodes=[
        {
            "x": 300,
            "y": 40,
            "w": 400,
            "h": 70,
            "style": "accent",
            "lines": ["Signal.publish(event)", "queued: nested events wait their turn"],
        },
        {
            "x": 300,
            "y": 160,
            "w": 400,
            "h": 70,
            "style": "box",
            "lines": ["subscribers", "a snapshot, in subscription order"],
        },
        {
            "x": 70,
            "y": 300,
            "w": 260,
            "h": 70,
            "style": "user",
            "lines": ["TrackingHistory.record", "bound method: held through WeakMethod"],
        },
        {
            "x": 370,
            "y": 300,
            "w": 260,
            "h": 70,
            "style": "user",
            "lines": ["lambda", "held strongly"],
        },
        {
            "x": 670,
            "y": 300,
            "w": 260,
            "h": 70,
            "style": "ink",
            "lines": ["a failing subscriber", "error collected, delivery continues"],
        },
        {
            "x": 330,
            "y": 450,
            "w": 340,
            "h": 70,
            "style": "accent",
            "lines": ["ExceptionGroup", "raised after every subscriber has run"],
        },
        {
            "x": 280,
            "y": 600,
            "w": 440,
            "h": 70,
            "style": "ghost",
            "lines": ["plain list", "stops at a failure, keeps every subscriber alive"],
        },
    ],
    edges=[
        {"x1": 500, "y1": 110, "x2": 500, "y2": 160},
        {"x1": 420, "y1": 230, "x2": 200, "y2": 300},
        {"x1": 500, "y1": 230, "x2": 500, "y2": 300},
        {"x1": 580, "y1": 230, "x2": 800, "y2": 300},
        {"x1": 200, "y1": 370, "x2": 420, "y2": 450},
        {"x1": 500, "y1": 370, "x2": 500, "y2": 450},
        {"x1": 800, "y1": 370, "x2": 580, "y2": 450},
    ],
)
