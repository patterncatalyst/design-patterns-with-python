"""Working with AI and LLM tools: a draft, three gates and the findings that go back."""

from generate_diagram import emit

emit(
    "40-working-with-ai-and-llm-tools",
    960,
    410,
    nodes=[
        {
            "h": 70,
            "lines": ["a draft's text", "Assistant.reply, or a file in tests/drafts"],
            "style": "box",
            "w": 900,
            "x": 30,
            "y": 20,
        },
        {
            "h": 80,
            "lines": ["static gate: mypy --strict, ruff", "reports untyped_factory"],
            "style": "box",
            "w": 290,
            "x": 30,
            "y": 190,
        },
        {
            "h": 80,
            "lines": [
                "shape review: review_gate.shape",
                "reports untyped_factory,",
                "typed_hierarchy",
            ],
            "style": "box",
            "w": 290,
            "x": 335,
            "y": 190,
        },
        {
            "h": 80,
            "lines": [
                "behaviour oracle: GRID",
                "reports untyped_factory,",
                "rounded_callable",
            ],
            "style": "box",
            "w": 290,
            "x": 640,
            "y": 190,
        },
        {
            "h": 70,
            "lines": ["accepted", "no gate reports the draft"],
            "style": "accent",
            "w": 900,
            "x": 30,
            "y": 330,
        },
    ],
    edges=[
        {"x1": 175, "x2": 175, "y1": 90, "y2": 190},
        {"x1": 440, "x2": 440, "y1": 90, "y2": 190},
        {"x1": 785, "x2": 785, "y1": 90, "y2": 190},
        {
            "amber": True,
            "label": "propose: every gate's findings go back in the next prompt",
            "lx": -26,
            "ly": 4,
            "x1": 632,
            "x2": 632,
            "y1": 190,
            "y2": 90,
        },
        {"x1": 175, "x2": 175, "y1": 270, "y2": 330},
        {"x1": 480, "x2": 480, "y1": 270, "y2": 330},
        {"x1": 785, "x2": 785, "y1": 270, "y2": 330},
    ],
)
