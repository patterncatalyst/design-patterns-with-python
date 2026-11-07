"""Working with AI and LLM tools: a reply, three gates and the findings that go back."""

from generate_diagram import emit

emit(
    "40-working-with-ai-and-llm-tools",
    960,
    500,
    nodes=[
        {
            "h": 70,
            "lines": ["a draft's text", "Assistant.reply, or a file in tests/drafts"],
            "style": "box",
            "w": 900,
            "x": 30,
            "y": 30,
        },
        {
            "h": 80,
            "lines": ["static gate: mypy --strict, ruff", "reports untyped_factory"],
            "style": "box",
            "w": 290,
            "x": 30,
            "y": 230,
        },
        {
            "h": 80,
            "lines": ["shape review: review_gate.shape", "reports typed_hierarchy"],
            "style": "box",
            "w": 290,
            "x": 335,
            "y": 230,
        },
        {
            "h": 80,
            "lines": ["behaviour oracle: GRID", "reports rounded_callable"],
            "style": "box",
            "w": 290,
            "x": 640,
            "y": 230,
        },
        {
            "h": 70,
            "lines": ["accepted", "no gate reports the draft"],
            "style": "accent",
            "w": 900,
            "x": 30,
            "y": 400,
        },
    ],
    edges=[
        {"x1": 175, "x2": 175, "y1": 100, "y2": 230},
        {"x1": 440, "x2": 440, "y1": 100, "y2": 230},
        {"x1": 785, "x2": 785, "y1": 100, "y2": 230},
        {
            "amber": True,
            "label": "propose: findings go back in the next prompt",
            "lx": 118,
            "ly": 0,
            "x1": 540,
            "x2": 540,
            "y1": 230,
            "y2": 100,
        },
        {"x1": 175, "x2": 175, "y1": 310, "y2": 400},
        {"x1": 480, "x2": 480, "y1": 310, "y2": 400},
        {"x1": 785, "x2": 785, "y1": 310, "y2": 400},
    ],
)
