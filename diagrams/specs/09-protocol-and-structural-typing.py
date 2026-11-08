"""One booking call, three checks: absence, shape and declaration.

The test fixture below the absence lane is a note, not a step: no code swaps it in.
"""

from generate_diagram import emit

LANE_W = 270
LANE_Y = 170
LANE_H = 96
LANES = [
    (20, ["absence", "find_gateway(code)", "-> CarrierGateway | None", "narrowed before use"]),
    (310, ["shape", "CarrierGateway", "compared where passed", "FastlineGateway, no base class"]),
    (600, ["declaration", "CarrierBase", "checked at construction", "AircoGateway"]),
]

nodes = [
    {
        "x": 290,
        "y": 30,
        "w": 310,
        "h": 56,
        "style": "accent",
        "lines": ["book_with(code, consignment)", "one call, three checks behind it"],
    },
    {
        "x": 20,
        "y": 330,
        "w": LANE_W,
        "h": 70,
        "style": "ink",
        "lines": ["_NullGateway (test fixture)", "absence hidden: accepted", "books nothing"],
    },
]
edges = []
for x, lines in LANES:
    nodes.append({"x": x, "y": LANE_Y, "w": LANE_W, "h": LANE_H, "style": "box", "lines": lines})
    edges.append({"x1": 445, "y1": 86, "x2": x + LANE_W // 2, "y2": LANE_Y})

emit("09-protocol-and-structural-typing", 890, 430, nodes=nodes, edges=edges)
