"""A composition root builds one adapter and injects it; consumers name small Protocols."""

from generate_diagram import emit

emit(
    "06-isp-dip-and-di-without-a-framework",
    820,
    560,
    nodes=[
        {
            "x": 230,
            "y": 30,
            "w": 360,
            "h": 56,
            "style": "accent",
            "lines": ["build_app(carrier)", "the composition root"],
        },
        {
            "x": 230,
            "y": 140,
            "w": 360,
            "h": 56,
            "style": "box",
            "lines": ["FastlineGateway or AircoGateway", "one adapter, no base class"],
        },
        {
            "x": 20,
            "y": 250,
            "w": 370,
            "h": 56,
            "style": "box",
            "lines": ["BookingService(gateway, audit)", "injected by the root"],
        },
        {
            "x": 430,
            "y": 250,
            "w": 370,
            "h": 56,
            "style": "box",
            "lines": ["partial(tracking_history, gateway=...)", "injected by the root"],
        },
        {
            "x": 20,
            "y": 360,
            "w": 370,
            "h": 56,
            "style": "accent",
            "lines": ["BookingGateway", "book, cancel"],
        },
        {
            "x": 430,
            "y": 360,
            "w": 370,
            "h": 56,
            "style": "accent",
            "lines": ["TrackingGateway", "track"],
        },
        {
            "x": 230,
            "y": 470,
            "w": 360,
            "h": 56,
            "style": "ink",
            "lines": ["The adapter satisfies both Protocols", "structurally, and imports neither"],
        },
    ],
    edges=[
        {"x1": 410, "y1": 86, "x2": 410, "y2": 140, "label": "builds", "lx": 30, "ly": 0},
        {"x1": 330, "y1": 196, "x2": 205, "y2": 250},
        {"x1": 490, "y1": 196, "x2": 615, "y2": 250},
        {"x1": 205, "y1": 306, "x2": 205, "y2": 360, "label": "names only", "lx": 50, "ly": 0},
        {"x1": 615, "y1": 306, "x2": 615, "y2": 360, "label": "names only", "lx": 50, "ly": 0},
        {"x1": 205, "y1": 416, "x2": 330, "y2": 470, "dashed": True},
        {"x1": 615, "y1": 416, "x2": 490, "y2": 470, "dashed": True},
    ],
)
