#!/usr/bin/env python3
"""Render every diagrams/specs/*.py into diagrams/<name>.svg and .excalidraw.

A spec is a small Python file that imports `emit` from `generate_diagram` and
calls it once, with the figure name equal to the spec's file stem. Specs are the
source of truth: never hand-edit the generated SVG.

    uv run python scripts/render_diagrams.py
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "diagrams" / "specs"
OUT = ROOT / "diagrams"


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import generate_diagram

    generate_diagram.OUT = OUT
    specs = sorted(SPECS.glob("*.py"))
    for spec in specs:
        runpy.run_path(str(spec), run_name="__spec__")
        for ext in (".svg", ".excalidraw"):
            if not (OUT / f"{spec.stem}{ext}").is_file():
                print(
                    f"render_diagrams: {spec.name} did not write {spec.stem}{ext}", file=sys.stderr
                )
                return 1
    print(f"rendered {len(specs)} diagram(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
