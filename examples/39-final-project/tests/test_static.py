"""What mypy reports when a gateway lacks a method the desk needs."""

import os
import re
from pathlib import Path

import mypy.api

_SRC = Path(__file__).resolve().parents[1] / "src"


def _run(snippet: str, tmp_path: Path) -> tuple[str, int]:
    """Type-check a snippet strictly, finding the package through the member's src directory."""
    config = tmp_path / "mypy.ini"
    config.write_text(f"[mypy]\nmypy_path = {_SRC}\n")
    stdout, _stderr, status = mypy.api.run(
        [
            "--strict",
            "--warn-unreachable",
            "--config-file",
            str(config),
            "--cache-dir",
            os.devnull,
            "--no-error-summary",
            "-c",
            snippet,
        ]
    )
    return stdout, status


def _codes(stdout: str) -> list[str]:
    return sorted(set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)))


# A gateway that can book but not cancel, handed to the desk.
_NO_CANCEL = """
from final_project.desk import BookingDesk
from final_project.domain import Consignment, HandlingEvent, Sailing
from final_project.rating import per_kg
from final_project.stowage import StowagePlan
from final_project.tracking import Signal


class BookOnly:
    def book(self, consignment: Consignment, /) -> str:
        return "ref"


desk = BookingDesk(
    rule=per_kg,
    plan=StowagePlan(Sailing("SAIL-1", "NLRTM", "SGSIN"), tiers=1),
    gateway=BookOnly(),
    events=Signal[HandlingEvent](),
)
"""
_CANCEL_METHOD = """
    def cancel(self, reference: str, /) -> None:
        return None
"""
_BOOK_BODY = '        return "ref"\n'
_WITH_CANCEL = _NO_CANCEL.replace(_BOOK_BODY, _BOOK_BODY + _CANCEL_METHOD)


def test_mypy_refuses_a_gateway_without_cancel(tmp_path: Path) -> None:
    """Credits the ``CarrierGateway`` annotation on ``BookingDesk``: annotating ``gateway`` as
    ``object`` makes the first list empty, and ``src`` then reports ``attr-defined``."""
    bare, bare_status = _run(_NO_CANCEL, tmp_path)
    complete, complete_status = _run(_WITH_CANCEL, tmp_path)

    assert [_codes(bare), _codes(complete)] == [["arg-type"], []]
    assert (bare_status, complete_status) == (1, 0)
    assert [line for line in bare.splitlines() if "[arg-type]" in line and "CarrierGateway" in line]
