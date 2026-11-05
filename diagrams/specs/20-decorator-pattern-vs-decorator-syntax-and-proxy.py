"""Two things called Decorator, and a proxy: a runtime stack, a definition-time rebinding."""

from generate_diagram import emit

LX = 40
LW = 380
RX = 580
RW = 380
LMID = LX + LW // 2
RMID = RX + RW // 2

emit(
    "20-decorator-pattern-vs-decorator-syntax-and-proxy",
    1000,
    700,
    bands=[
        {"x": 60, "y": 270, "w": 340, "h": 240, "label": "Tax", "fill": "#f4f4f4"},
        {"x": 85, "y": 310, "w": 290, "h": 170, "label": "Surcharge", "fill": "#ececec"},
    ],
    nodes=[
        {
            "x": LX,
            "y": 50,
            "w": LW,
            "h": 70,
            "style": "user",
            "lines": ["layers_for(consignment)", "chooses the layers for this consignment"],
        },
        {
            "x": LX,
            "y": 160,
            "w": LW,
            "h": 70,
            "style": "user",
            "lines": ["compose(base, layers)", "the last layer ends up outermost"],
        },
        {
            "x": 115,
            "y": 360,
            "w": 230,
            "h": 70,
            "style": "box",
            "lines": ["BaseRate", "innermost: the base price"],
        },
        {
            "x": RX,
            "y": 50,
            "w": RW,
            "h": 70,
            "style": "ink",
            "lines": ["@retry(attempts=..., on=...)", "a factory returns the decorator"],
        },
        {
            "x": RX,
            "y": 160,
            "w": RW,
            "h": 70,
            "style": "ink",
            "lines": ["def quote_carrier", "the function the line above wraps"],
        },
        {
            "x": RX,
            "y": 270,
            "w": RW,
            "h": 70,
            "style": "ink",
            "lines": ["quote_carrier", "name rebound once, when the module loads"],
        },
        {
            "x": 440,
            "y": 160,
            "w": 120,
            "h": 70,
            "style": "ghost",
            "lines": ["same word,", "unrelated", "mechanisms"],
        },
        {
            "x": LX,
            "y": 590,
            "w": 520,
            "h": 70,
            "style": "accent",
            "lines": [
                "CarrierGatewayProxy",
                "Proxy: same interface, controls access (caches quote)",
            ],
        },
        {
            "x": 620,
            "y": 590,
            "w": 340,
            "h": 70,
            "style": "ghost",
            "lines": ["forwarding with __getattr__", "mypy sees Any"],
        },
    ],
    edges=[
        {"x1": LMID, "y1": 120, "x2": LMID, "y2": 160},
        {"x1": LMID, "y1": 230, "x2": LMID, "y2": 270},
        {"x1": RMID, "y1": 120, "x2": RMID, "y2": 160},
        {"x1": RMID, "y1": 230, "x2": RMID, "y2": 270},
    ],
    notes=[
        {
            "x": LX,
            "y": 32,
            "text": "Decorator pattern: while the program runs",
            "color": "#111111",
            "size": 13,
            "bold": True,
        },
        {
            "x": RX,
            "y": 32,
            "text": "@decorator syntax: at definition time",
            "color": "#111111",
            "size": 13,
            "bold": True,
        },
        {
            "x": LMID,
            "y": 540,
            "text": "a value: chosen per consignment",
            "anchor": "middle",
            "color": "#555555",
            "size": 12,
        },
    ],
)
