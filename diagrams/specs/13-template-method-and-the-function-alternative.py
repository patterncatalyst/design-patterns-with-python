"""One customs skeleton, two ways to vary it: a hooks record or a final template on a base class."""

from itertools import pairwise

from generate_diagram import emit

STEP_X = 340
STEP_W = 250
STEP_H = 50
STEPS = [
    ("ink", ["refuse no commodities", "invariant"]),
    ("user", ["classify each commodity", "hook"]),
    ("ink", ["total in one currency", "invariant"]),
    ("user", ["assess duty", "hook"]),
    ("ink", ["commercial invoice first", "invariant, then extra documents"]),
]
STEP_Y = [140, 230, 320, 410, 500]

nodes = [
    {
        "x": STEP_X,
        "y": 30,
        "w": STEP_W,
        "h": 56,
        "style": "accent",
        "lines": ["declare_customs", "(consignment, hooks=...)"],
    },
    {
        "x": 20,
        "y": 30,
        "w": 280,
        "h": 56,
        "style": "box",
        "lines": ["CustomsHooks", "functions per destination (SINGAPORE)"],
    },
    {
        "x": 620,
        "y": 30,
        "w": 340,
        "h": 70,
        "style": "box",
        "lines": [
            "CustomsDeclarer",
            "@final declare, shared schedule",
            "bound methods become hooks",
        ],
    },
    {
        "x": 620,
        "y": 160,
        "w": 165,
        "h": 50,
        "style": "box",
        "lines": ["NetherlandsDeclarer"],
    },
    {
        "x": 795,
        "y": 160,
        "w": 165,
        "h": 50,
        "style": "box",
        "lines": ["GermanyDeclarer"],
    },
    {
        "x": 670,
        "y": 500,
        "w": 290,
        "h": STEP_H,
        "style": "box",
        "lines": ["extra_documents", "default: none"],
    },
    {
        "x": STEP_X,
        "y": 610,
        "w": STEP_W,
        "h": 56,
        "style": "accent",
        "lines": ["CustomsDeclaration", "lines, value, duty, documents"],
    },
]
for (style, lines), y in zip(STEPS, STEP_Y, strict=True):
    nodes.append({"x": STEP_X, "y": y, "w": STEP_W, "h": STEP_H, "style": style, "lines": lines})

edges = [
    {"x1": 300, "y1": 58, "x2": STEP_X, "y2": 58},
    {"x1": 620, "y1": 58, "x2": STEP_X + STEP_W, "y2": 58},
    {"x1": 702, "y1": 160, "x2": 702, "y2": 100},
    {"x1": 877, "y1": 160, "x2": 877, "y2": 100},
    {"x1": 670, "y1": 525, "x2": STEP_X + STEP_W, "y2": 525},
    {"x1": 465, "y1": 86, "x2": 465, "y2": 140},
    {"x1": 465, "y1": 550, "x2": 465, "y2": 610},
]
for a, b in pairwise(STEP_Y):
    edges.append({"x1": 465, "y1": a + STEP_H, "x2": 465, "y2": b})

emit("13-template-method-and-the-function-alternative", 980, 700, nodes=nodes, edges=edges)
