"""A booking request from a template: copy, construct, validate, and the field-type caveat."""

from generate_diagram import emit

X = 280
W = 400
MID = X + W // 2

emit(
    "17-builder-dataclasses-and-prototype",
    990,
    700,
    nodes=[
        {
            "x": X,
            "y": 30,
            "w": W,
            "h": 70,
            "style": "box",
            "lines": ["TEMPLATES", "read-only: name to template request"],
        },
        {
            "x": X,
            "y": 150,
            "w": W,
            "h": 70,
            "style": "ink",
            "lines": ["from_template", "replace(template, ...)"],
        },
        {
            "x": X,
            "y": 270,
            "w": W,
            "h": 70,
            "style": "user",
            "lines": ["BookingRequest(...)", "keyword-only, frozen"],
        },
        {
            "x": X,
            "y": 390,
            "w": W,
            "h": 84,
            "style": "box",
            "lines": ["__post_init__", "cross-field checks: insured,", "dangerous goods, ports"],
        },
        {
            "x": 730,
            "y": 390,
            "w": 240,
            "h": 84,
            "style": "ghost",
            "lines": ["every copy path", "reruns it:", "replace, copy.replace"],
        },
        {
            "x": X,
            "y": 540,
            "w": W,
            "h": 84,
            "style": "accent",
            "lines": ["a list field is shared", "by copy and replace;", "a tuple field cannot be"],
        },
    ],
    edges=[
        {"x1": MID, "y1": 100, "x2": MID, "y2": 150},
        {"x1": MID, "y1": 220, "x2": MID, "y2": 270},
        {"x1": MID, "y1": 340, "x2": MID, "y2": 390},
        {"x1": X + W, "y1": 432, "x2": 730, "y2": 432, "dashed": True},
        {"x1": MID, "y1": 474, "x2": MID, "y2": 540, "dashed": True},
    ],
)
