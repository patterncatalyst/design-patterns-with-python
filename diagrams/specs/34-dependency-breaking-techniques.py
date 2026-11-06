"""Dependency-breaking techniques: four forms of the engine under one characterisation table."""

from generate_diagram import emit

emit(
    "34-dependency-breaking-techniques",
    1300,
    520,
    nodes=[
        {
            "x": 40,
            "y": 30,
            "w": 420,
            "h": 70,
            "style": "box",
            "lines": ["legacy", "enabling point: a patch on request_quote and airco.price"],
        },
        {
            "x": 80,
            "y": 160,
            "w": 420,
            "h": 70,
            "style": "box",
            "lines": ["parameterised", "keyword parameters; defaults are the real calls"],
        },
        {
            "x": 120,
            "y": 290,
            "w": 420,
            "h": 70,
            "style": "box",
            "lines": ["wrapped", "airco_quote fits CarrierQuoter"],
        },
        {
            "x": 160,
            "y": 420,
            "w": 420,
            "h": 70,
            "style": "accent",
            "lines": ["rating.quote", "quoters required; quote_standard binds them"],
        },
        {
            "x": 680,
            "y": 30,
            "w": 230,
            "h": 460,
            "style": "ink",
            "lines": ["same characterisation table"],
        },
        {
            "x": 960,
            "y": 190,
            "w": 300,
            "h": 110,
            "style": "ghost",
            "lines": [
                "subclass and override",
                "also passes the same table;",
                "overridden method names are the seam;",
                "mypy reports a typo only with @override",
            ],
        },
    ],
    edges=[
        {"x1": 150, "y1": 100, "x2": 150, "y2": 160, "label": "one technique", "lx": 55},
        {"x1": 190, "y1": 230, "x2": 190, "y2": 290, "label": "one technique", "lx": 55},
        {"x1": 230, "y1": 360, "x2": 230, "y2": 420, "label": "one technique", "lx": 55},
        {"x1": 680, "y1": 65, "x2": 460, "y2": 65},
        {"x1": 680, "y1": 195, "x2": 500, "y2": 195},
        {"x1": 680, "y1": 325, "x2": 540, "y2": 325},
        {"x1": 680, "y1": 455, "x2": 580, "y2": 455},
        {"x1": 960, "y1": 245, "x2": 910, "y2": 245, "dashed": True},
    ],
)
