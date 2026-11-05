"""Facade, Bridge and Adapter: one call, two axes, one translation."""

from generate_diagram import emit

CX = 460

emit(
    "19-adapter-facade-bridge",
    1100,
    700,
    nodes=[
        {
            "x": CX - 190,
            "y": 30,
            "w": 380,
            "h": 70,
            "style": "accent",
            "lines": ["ship(consignment, carrier, ...)", "Facade: one call, domain types only"],
        },
        {
            "x": 110,
            "y": 160,
            "w": 260,
            "h": 70,
            "style": "user",
            "lines": ["StandardBooking", "Bridge: each kind holds a gateway"],
        },
        {
            "x": 550,
            "y": 160,
            "w": 260,
            "h": 70,
            "style": "user",
            "lines": ["InsuredBooking", "Bridge: each kind holds a gateway"],
        },
        {
            "x": CX - 190,
            "y": 290,
            "w": 380,
            "h": 70,
            "style": "box",
            "lines": ["CarrierGateway", "book, insure: the narrow Protocol"],
        },
        {
            "x": 90,
            "y": 420,
            "w": 300,
            "h": 70,
            "style": "box",
            "lines": ["AircoClient", "shape already matches: no adapter"],
        },
        {
            "x": 530,
            "y": 420,
            "w": 300,
            "h": 70,
            "style": "ink",
            "lines": ["FastlineGateway", "Adapter: shape, pounds, errors"],
        },
        {
            "x": 530,
            "y": 560,
            "w": 300,
            "h": 70,
            "style": "ghost",
            "lines": ["FastlineClient", "carrier SDK"],
        },
        {
            "x": 880,
            "y": 420,
            "w": 200,
            "h": 70,
            "style": "ghost",
            "lines": ["Weight.pounds", "units converted in one place"],
        },
    ],
    edges=[
        {"x1": CX - 100, "y1": 100, "x2": 240, "y2": 160},
        {"x1": CX + 100, "y1": 100, "x2": 680, "y2": 160},
        {"x1": 240, "y1": 230, "x2": CX - 100, "y2": 290},
        {"x1": 680, "y1": 230, "x2": CX + 100, "y2": 290},
        {"x1": CX - 100, "y1": 360, "x2": 240, "y2": 420},
        {"x1": CX + 100, "y1": 360, "x2": 680, "y2": 420},
        {"x1": 680, "y1": 490, "x2": 680, "y2": 560},
        {"x1": 880, "y1": 455, "x2": 830, "y2": 455, "dashed": True},
    ],
)
