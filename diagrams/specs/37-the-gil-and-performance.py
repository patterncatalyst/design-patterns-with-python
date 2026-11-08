"""The GIL and performance: two threads reserve a slot, with and without a lock."""

from generate_diagram import emit

emit(
    "37-the-gil-and-performance",
    860,
    560,
    nodes=[
        {
            "x": 230,
            "y": 30,
            "w": 400,
            "h": 70,
            "style": "box",
            "lines": ["StowagePlan.reserve", "pick slot, gap, store"],
        },
        {
            "x": 40,
            "y": 180,
            "w": 360,
            "h": 80,
            "style": "sub",
            "lines": ["no lock: nullcontext", "two threads meet in the gap (Barrier)"],
        },
        {
            "x": 460,
            "y": 180,
            "w": 360,
            "h": 80,
            "style": "accent",
            "lines": [
                "Lock over the read and the write",
                "_RecordingLock: the second caller waits",
            ],
        },
        {
            "x": 40,
            "y": 330,
            "w": 360,
            "h": 80,
            "style": "ghost",
            "lines": [
                "the two threads take the same SlotId",
                "on either build; one reservation is left",
            ],
        },
        {
            "x": 460,
            "y": 330,
            "w": 360,
            "h": 80,
            "style": "accent",
            "lines": ["each thread gets its own SlotId", "two reservations are stored"],
        },
        {
            "x": 40,
            "y": 470,
            "w": 780,
            "h": 60,
            "style": "ink",
            "lines": [
                "a lock that covers the read and the write keeps the pair together",
                "the GIL does not join them",
            ],
        },
    ],
    edges=[
        {"x1": 330, "y1": 100, "x2": 220, "y2": 180},
        {"x1": 530, "y1": 100, "x2": 640, "y2": 180},
        {"x1": 220, "y1": 260, "x2": 220, "y2": 330, "dashed": True},
        {"x1": 640, "y1": 260, "x2": 640, "y2": 330},
    ],
)
