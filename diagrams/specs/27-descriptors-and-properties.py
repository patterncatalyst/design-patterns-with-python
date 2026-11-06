"""Descriptors and properties: one Positive descriptor, the lookup order, a cached property."""

from generate_diagram import emit

emit(
    "27-descriptors-and-properties",
    1000,
    760,
    nodes=[
        {
            "x": 300,
            "y": 30,
            "w": 400,
            "h": 100,
            "style": "accent",
            "lines": [
                "Positive",
                "__set_name__: learns the field name",
                "__get__: reads the stored value",
                "__set__: validates, stores in vars()",
            ],
        },
        {
            "x": 40,
            "y": 230,
            "w": 280,
            "h": 60,
            "style": "user",
            "lines": ["Consignment", "kilograms"],
        },
        {
            "x": 360,
            "y": 230,
            "w": 280,
            "h": 60,
            "style": "user",
            "lines": ["Dimensions", "length_cm, width_cm, height_cm"],
        },
        {
            "x": 680,
            "y": 230,
            "w": 280,
            "h": 60,
            "style": "user",
            "lines": ["Container", "tare_kg, max_payload_kg"],
        },
        {
            "x": 40,
            "y": 390,
            "w": 400,
            "h": 60,
            "style": "box",
            "lines": ["data descriptor", "Positive, property"],
        },
        {
            "x": 40,
            "y": 500,
            "w": 400,
            "h": 60,
            "style": "box",
            "lines": ["instance __dict__"],
        },
        {
            "x": 40,
            "y": 610,
            "w": 400,
            "h": 60,
            "style": "box",
            "lines": ["non-data descriptor", "cached_property"],
        },
        {
            "x": 560,
            "y": 595,
            "w": 400,
            "h": 90,
            "style": "accent",
            "lines": [
                "chargeable_kg",
                "cached_property: computed on first read,",
                "then read from __dict__",
            ],
        },
        {
            "x": 560,
            "y": 420,
            "w": 400,
            "h": 60,
            "style": "ghost",
            "lines": ["slots=True", "a slot replaces the descriptor"],
        },
    ],
    edges=[
        {"x1": 440, "y1": 130, "x2": 180, "y2": 230},
        {"x1": 500, "y1": 130, "x2": 500, "y2": 230},
        {"x1": 560, "y1": 130, "x2": 820, "y2": 230},
        {"x1": 240, "y1": 450, "x2": 240, "y2": 500},
        {"x1": 240, "y1": 560, "x2": 240, "y2": 610},
        {"x1": 560, "y1": 640, "x2": 440, "y2": 640},
    ],
    notes=[
        {
            "x": 40,
            "y": 372,
            "text": "attribute lookup on an instance",
            "bold": True,
            "color": "#555",
        },
    ],
)
