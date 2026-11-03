"""The local toolchain loop a reader runs against an example."""

from generate_diagram import emit

MAIN_X, MAIN_W = 230, 350
ROWS = [116, 202, 288, 374]  # uv sync, ruff, mypy, pytest
H = 56

emit(
    "00-prerequisites",
    820,
    540,
    nodes=[
        {
            "x": 20,
            "y": 30,
            "w": 780,
            "h": H,
            "style": "box",
            "lines": ["Edit the source", "src/consignments/consignment.py"],
        },
        {
            "x": MAIN_X,
            "y": ROWS[0],
            "w": MAIN_W,
            "h": H,
            "style": "accent",
            "lines": [
                "uv sync --locked --all-packages",
                "one interpreter, one lockfile, one .venv",
            ],
        },
        {
            "x": MAIN_X,
            "y": ROWS[1],
            "w": MAIN_W,
            "h": H,
            "style": "box",
            "lines": ["ruff check, ruff format --check", "lint and formatting"],
        },
        {
            "x": MAIN_X,
            "y": ROWS[2],
            "w": MAIN_W,
            "h": H,
            "style": "box",
            "lines": ["mypy --strict src tests", "the build gate"],
        },
        {
            "x": MAIN_X,
            "y": ROWS[3],
            "w": MAIN_W,
            "h": H,
            "style": "box",
            "lines": ["pytest", "tests on Consignment, ConsignmentId, Weight"],
        },
        {
            "x": MAIN_X,
            "y": 460,
            "w": MAIN_W,
            "h": H,
            "style": "ink",
            "lines": ["green", "the example is ready to build on"],
        },
        {
            "x": 20,
            "y": ROWS[1],
            "w": 160,
            "h": ROWS[3] + H - ROWS[1],
            "style": "ghost",
            "lines": ["red", "fix the source", "and rerun"],
        },
        {
            "x": 610,
            "y": ROWS[0] - 6,
            "w": 200,
            "h": H + 12,
            "style": "sub",
            "lines": ["scripts/check-prereqs.sh", "gates the toolchain first"],
        },
    ],
    edges=[
        {"x1": 405, "y1": 86, "x2": 405, "y2": ROWS[0]},
        {"x1": 405, "y1": ROWS[0] + H, "x2": 405, "y2": ROWS[1]},
        {"x1": 405, "y1": ROWS[1] + H, "x2": 405, "y2": ROWS[2]},
        {"x1": 405, "y1": ROWS[2] + H, "x2": 405, "y2": ROWS[3]},
        {"x1": 405, "y1": ROWS[3] + H, "x2": 405, "y2": 460, "label": "pass", "lx": 20, "ly": 4},
        {"x1": 610, "y1": ROWS[0] + H / 2, "x2": MAIN_X + MAIN_W, "y2": ROWS[0] + H / 2},
        {"x1": MAIN_X, "y1": ROWS[1] + H / 2, "x2": 180, "y2": ROWS[1] + H / 2, "amber": True},
        {"x1": MAIN_X, "y1": ROWS[2] + H / 2, "x2": 180, "y2": ROWS[2] + H / 2, "amber": True},
        {"x1": MAIN_X, "y1": ROWS[3] + H / 2, "x2": 180, "y2": ROWS[3] + H / 2, "amber": True},
        {"x1": 100, "y1": ROWS[1], "x2": 100, "y2": 86, "amber": True, "dashed": True},
    ],
)
