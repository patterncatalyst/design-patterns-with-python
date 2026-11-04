"""One quote, three responsibilities: pricing, tax and audit."""

from generate_diagram import emit

emit(
    "05-srp-ocp-lsp",
    820,
    560,
    nodes=[
        {
            "x": 190,
            "y": 30,
            "w": 440,
            "h": 56,
            "style": "accent",
            "lines": ["quote", "the coordinator: one consignment in, one RateQuote out"],
        },
        {
            "x": 190,
            "y": 140,
            "w": 440,
            "h": 56,
            "style": "box",
            "lines": ["RateCalculator: BaseRate or FlatRate", "pricing changes with the tariff"],
        },
        {
            "x": 190,
            "y": 250,
            "w": 440,
            "h": 56,
            "style": "box",
            "lines": ["TAX_RULES: percent by destination country", "tax changes with tax law"],
        },
        {
            "x": 190,
            "y": 360,
            "w": 440,
            "h": 56,
            "style": "ink",
            "lines": ["RateQuote", "net from pricing, tax computed on that net"],
        },
        {
            "x": 190,
            "y": 470,
            "w": 440,
            "h": 56,
            "style": "box",
            "lines": ["AuditSink: a callable", "audit changes with compliance"],
        },
        {
            "x": 660,
            "y": 140,
            "w": 140,
            "h": 56,
            "style": "kernel",
            "lines": ["Contract suite", "every calculator"],
        },
    ],
    edges=[
        {"x1": 410, "y1": 86, "x2": 410, "y2": 140},
        {"x1": 410, "y1": 196, "x2": 410, "y2": 250, "label": "net", "lx": 16, "ly": 0},
        {"x1": 410, "y1": 306, "x2": 410, "y2": 360, "label": "tax", "lx": 16, "ly": 0},
        {"x1": 410, "y1": 416, "x2": 410, "y2": 470, "label": "finished quote", "lx": 50, "ly": 0},
        {"x1": 660, "y1": 168, "x2": 630, "y2": 168, "dashed": True},
    ],
)
