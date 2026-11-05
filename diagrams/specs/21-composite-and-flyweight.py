"""Composite and Flyweight: one weight question through a tree, one shared commodity per code."""

from generate_diagram import emit

emit(
    "21-composite-and-flyweight",
    1040,
    700,
    nodes=[
        {
            "x": 250,
            "y": 40,
            "w": 300,
            "h": 70,
            "style": "accent",
            "lines": ["ConsolidatedShipment", "weight: sums its parts, nested or not"],
        },
        {
            "x": 50,
            "y": 290,
            "w": 200,
            "h": 70,
            "style": "user",
            "lines": ["Consignment", "a leaf: its own weight"],
        },
        {
            "x": 400,
            "y": 160,
            "w": 250,
            "h": 70,
            "style": "accent",
            "lines": ["ConsolidatedShipment", "a nested group, same question"],
        },
        {
            "x": 300,
            "y": 290,
            "w": 200,
            "h": 70,
            "style": "user",
            "lines": ["Consignment", "a leaf: its own weight"],
        },
        {
            "x": 550,
            "y": 290,
            "w": 200,
            "h": 70,
            "style": "user",
            "lines": ["Consignment", "a leaf: its own weight"],
        },
        {
            "x": 250,
            "y": 430,
            "w": 300,
            "h": 70,
            "style": "box",
            "lines": ["Commodity", "one object per code, frozen"],
        },
        {
            "x": 200,
            "y": 570,
            "w": 400,
            "h": 70,
            "style": "box",
            "lines": ["CommodityPool", "weak values: dropped when nobody holds them"],
        },
        {
            "x": 770,
            "y": 430,
            "w": 240,
            "h": 70,
            "style": "ink",
            "lines": ["port_code", "sys.intern: one object per code"],
        },
    ],
    edges=[
        {"x1": 330, "y1": 110, "x2": 150, "y2": 290},
        {"x1": 470, "y1": 110, "x2": 525, "y2": 160},
        {"x1": 480, "y1": 230, "x2": 400, "y2": 290},
        {"x1": 570, "y1": 230, "x2": 650, "y2": 290},
        {"x1": 150, "y1": 360, "x2": 330, "y2": 430},
        {"x1": 400, "y1": 360, "x2": 400, "y2": 430},
        {"x1": 650, "y1": 360, "x2": 470, "y2": 430},
        {"x1": 400, "y1": 570, "x2": 400, "y2": 500},
    ],
    notes=[
        {
            "x": 620,
            "y": 80,
            "text": "Shipment = Consignment | ConsolidatedShipment",
            "color": "#555555",
            "size": 12,
        },
    ],
)
