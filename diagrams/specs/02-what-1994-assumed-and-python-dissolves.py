"""What the 1994 catalogue assumed, paired with the Python feature that removes it."""

from generate_diagram import emit

ROWS = [
    (
        ["Behaviour travels inside an object", "one rule class per pricing variant"],
        ["PricingRule, per_kg", "functions are objects"],
    ),
    (
        ["A shared interface is declared", "by inheriting from a base class"],
        ["CarrierGateway", "structural typing through a Protocol"],
    ),
    (
        ["Traversal needs its own object", "to hold the position"],
        ["pages", "a generator pulls one page at a time"],
    ),
    (
        ["One instance needs a guarded class", "with a private constructor"],
        ["tariff_table", "a module is imported once, TARIFF built then"],
    ),
    (
        ["Absence needs a stand-in object", "that does nothing"],
        ["CarrierGateway | None", "find_gateway, checked by the type checker"],
    ),
]

Y0, STEP, H = 70, 86, 60
nodes = []
edges = []
for i, (old, new) in enumerate(ROWS):
    y = Y0 + i * STEP
    nodes.append({"x": 20, "y": y, "w": 330, "h": H, "style": "box", "lines": old})
    nodes.append({"x": 470, "y": y, "w": 330, "h": H, "style": "accent", "lines": new})
    edges.append(
        {"x1": 350, "y1": y + H / 2, "x2": 470, "y2": y + H / 2, "label": "becomes", "ly": -8}
    )

emit(
    "02-what-1994-assumed-and-python-dissolves",
    820,
    Y0 + 5 * STEP + 10,
    nodes=nodes,
    edges=edges,
    notes=[
        {
            "x": 185,
            "y": 40,
            "text": "Assumed in 1994",
            "size": 13,
            "bold": True,
            "color": "#111111",
            "anchor": "middle",
        },
        {
            "x": 635,
            "y": 40,
            "text": "What Python gives you",
            "size": 13,
            "bold": True,
            "color": "#111111",
            "anchor": "middle",
        },
    ],
)
