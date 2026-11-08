"""Both ways out of a manifest write: __exit__ commits on success and discards on failure."""

from generate_diagram import emit

emit(
    "10-context-managers",
    820,
    600,
    nodes=[
        {
            "x": 230,
            "y": 30,
            "w": 360,
            "h": 56,
            "style": "accent",
            "lines": ["with ManifestWriter(path) as out:", "the block begins"],
        },
        {
            "x": 230,
            "y": 130,
            "w": 360,
            "h": 56,
            "style": "box",
            "lines": ["__enter__", "opens path.partial"],
        },
        {
            "x": 230,
            "y": 230,
            "w": 360,
            "h": 56,
            "style": "box",
            "lines": ["body writes lines", "to the partial file"],
        },
        {
            "x": 20,
            "y": 360,
            "w": 360,
            "h": 76,
            "style": "box",
            "lines": [
                "body returns",
                "__exit__(None, None, None)",
                "close, replace partial with path",
            ],
        },
        {
            "x": 440,
            "y": 360,
            "w": 360,
            "h": 76,
            "style": "box",
            "lines": [
                "body raises",
                "__exit__(exc_type, exc, traceback)",
                "close, unlink partial, return None",
            ],
        },
        {
            "x": 20,
            "y": 490,
            "w": 360,
            "h": 56,
            "style": "ink",
            "lines": ["manifest committed", "readers see the complete file"],
        },
        {
            "x": 440,
            "y": 490,
            "w": 360,
            "h": 56,
            "style": "accent",
            "lines": ["exception propagates", "no partial file is left behind"],
        },
    ],
    edges=[
        {"x1": 410, "y1": 86, "x2": 410, "y2": 130},
        {"x1": 410, "y1": 186, "x2": 410, "y2": 230},
        {"x1": 410, "y1": 286, "x2": 200, "y2": 360},
        {"x1": 410, "y1": 286, "x2": 620, "y2": 360},
        {"x1": 200, "y1": 436, "x2": 200, "y2": 490},
        {"x1": 620, "y1": 436, "x2": 620, "y2": 490},
    ],
)
