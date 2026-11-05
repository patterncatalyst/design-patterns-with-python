"""Iterator: a fresh iterator per loop, lazy pages, and a reader that closes its file."""

from generate_diagram import emit

emit(
    "24-iterator-generators-and-the-iterator-protocol",
    1000,
    660,
    nodes=[
        {
            "x": 100,
            "y": 30,
            "w": 300,
            "h": 70,
            "style": "accent",
            "lines": ["TrackingHistory", "each loop gets a fresh iterator"],
        },
        {"x": 30, "y": 180, "w": 180, "h": 60, "style": "user", "lines": ["__iter__", "walk one"]},
        {"x": 240, "y": 180, "w": 180, "h": 60, "style": "user", "lines": ["__iter__", "walk two"]},
        {
            "x": 460,
            "y": 180,
            "w": 220,
            "h": 70,
            "style": "ghost",
            "lines": ["self-iterating cursor", "empty on the second pass"],
        },
        {
            "x": 80,
            "y": 340,
            "w": 340,
            "h": 70,
            "style": "box",
            "lines": ["pages", "batched: reads one page at a time"],
        },
        {
            "x": 80,
            "y": 480,
            "w": 340,
            "h": 70,
            "style": "box",
            "lines": ["page", "islice: stops at the page it returns"],
        },
        {
            "x": 710,
            "y": 180,
            "w": 260,
            "h": 70,
            "style": "accent",
            "lines": ["read_events", "opens inside with"],
        },
        {
            "x": 710,
            "y": 340,
            "w": 260,
            "h": 70,
            "style": "user",
            "lines": ["close()", "file closed, reader finished"],
        },
        {
            "x": 710,
            "y": 480,
            "w": 260,
            "h": 70,
            "style": "ghost",
            "lines": ["break alone", "still open while named"],
        },
    ],
    edges=[
        {"x1": 220, "y1": 100, "x2": 120, "y2": 180},
        {"x1": 280, "y1": 100, "x2": 330, "y2": 180},
        {"x1": 120, "y1": 240, "x2": 200, "y2": 340},
        {"x1": 330, "y1": 240, "x2": 300, "y2": 340},
        {"x1": 250, "y1": 410, "x2": 250, "y2": 480},
        {"x1": 840, "y1": 250, "x2": 840, "y2": 340},
    ],
)
