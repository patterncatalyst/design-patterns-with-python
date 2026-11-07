"""asyncio and the patterns: a session, a feed, subscribers, quotes and commands on one loop."""

from generate_diagram import emit

emit(
    "38-asyncio-and-the-patterns",
    980,
    640,
    nodes=[
        {
            "x": 40,
            "y": 30,
            "w": 400,
            "h": 70,
            "style": "accent",
            "lines": ["carrier_session", "open the feed; close it when the body ends"],
        },
        {
            "x": 40,
            "y": 160,
            "w": 400,
            "h": 70,
            "style": "box",
            "lines": ["handling_events", "an async generator over the feed"],
        },
        {
            "x": 40,
            "y": 290,
            "w": 400,
            "h": 70,
            "style": "box",
            "lines": [
                "AsyncSignal.publish",
                "gather runs the subscribers; failures raise as a group",
            ],
        },
        {
            "x": 40,
            "y": 420,
            "w": 400,
            "h": 70,
            "style": "ghost",
            "lines": ["_TaskGroupSignal", "one failing subscriber cancels the rest"],
        },
        {
            "x": 540,
            "y": 160,
            "w": 400,
            "h": 80,
            "style": "box",
            "lines": [
                "cheapest",
                "TaskGroup over RateSource",
                "AircoSource runs the SDK in a thread",
            ],
        },
        {
            "x": 540,
            "y": 330,
            "w": 400,
            "h": 70,
            "style": "box",
            "lines": ["run_commands", "a Queue until shutdown"],
        },
        {
            "x": 40,
            "y": 550,
            "w": 900,
            "h": 60,
            "style": "ink",
            "lines": [
                "an await is where another task can run",
                "cancellation still closes the feed",
            ],
        },
    ],
    edges=[
        {"x1": 240, "y1": 360, "x2": 240, "y2": 420, "dashed": True},
    ],
)
