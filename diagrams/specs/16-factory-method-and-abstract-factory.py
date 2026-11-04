"""Carrier kits: a read-only registry, one kit per family, and what the types tie together."""

from generate_diagram import emit

KIT_W = 300
LEFT_X = 300
RIGHT_X = 660
KIT_Y = 270
GW_Y = 380
LP_Y = 500
RT_Y = 620

nodes = [
    {"x": 480, "y": 30, "w": 300, "h": 56, "style": "accent", "lines": ["ship(code, ...)"]},
    {
        "x": 480,
        "y": 140,
        "w": 300,
        "h": 70,
        "style": "box",
        "lines": ["KITS", "read-only: carrier code to kit"],
    },
    {
        "x": 20,
        "y": 270,
        "w": 230,
        "h": 76,
        "style": "box",
        "lines": ["GATEWAYS", "Factory Method: a constructor", "in a Callable slot"],
    },
    {
        "x": 20,
        "y": 480,
        "w": 230,
        "h": 76,
        "style": "ghost",
        "lines": ["mypy ties the gateway", "to the label printer", "by the reference type"],
    },
]
for x, kit, gateway, printer, rates in [
    (LEFT_X, "FASTLINE_KIT", "FastlineGateway", "FastlineLabelPrinter", "FastlineRates"),
    (RIGHT_X, "AIRCO_KIT", "AircoGateway", "AircoLabelPrinter", "AircoRates"),
]:
    nodes += [
        {"x": x, "y": KIT_Y, "w": KIT_W, "h": 56, "style": "ink", "lines": [kit]},
        {"x": x, "y": GW_Y, "w": KIT_W, "h": 56, "style": "user", "lines": [gateway]},
        {"x": x, "y": LP_Y, "w": KIT_W, "h": 56, "style": "user", "lines": [printer]},
        {
            "x": x,
            "y": RT_Y,
            "w": KIT_W,
            "h": 70,
            "style": "ghost",
            "lines": [rates, "not tied: one kit value", "keeps it consistent"],
        },
    ]

L_MID = LEFT_X + KIT_W // 2
R_MID = RIGHT_X + KIT_W // 2
edges = [
    {"x1": 630, "y1": 86, "x2": 630, "y2": 140},
    {"x1": 560, "y1": 210, "x2": L_MID, "y2": KIT_Y},
    {"x1": 700, "y1": 210, "x2": R_MID, "y2": KIT_Y},
    {"x1": L_MID, "y1": KIT_Y + 56, "x2": L_MID, "y2": GW_Y},
    {"x1": R_MID, "y1": KIT_Y + 56, "x2": R_MID, "y2": GW_Y},
    {"x1": L_MID, "y1": GW_Y + 56, "x2": L_MID, "y2": LP_Y, "label": "FastlineReference"},
    {"x1": R_MID, "y1": GW_Y + 56, "x2": R_MID, "y2": LP_Y, "label": "AircoReference"},
    {"x1": 135, "y1": 346, "x2": LEFT_X, "y2": GW_Y + 28, "dashed": True},
    {"x1": 250, "y1": 518, "x2": LEFT_X, "y2": LP_Y + 28, "dashed": True},
]

emit("16-factory-method-and-abstract-factory", 1000, 730, nodes=nodes, edges=edges)
