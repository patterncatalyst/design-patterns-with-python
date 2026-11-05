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


def _codes(stdout: str) -> set[str]:
    return set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE))


_STAGE_THAT_CAN_PASS_AS_FINAL = """
from mediator_chain.clearance import CLEARANCE_STAGES, Decision, clear
from mediator_chain.domain import CustomsDeclaration


def maybe(declaration: CustomsDeclaration, /) -> Decision | None: ...


def run(declaration: CustomsDeclaration) -> Decision:
    return clear(declaration, CLEARANCE_STAGES, final=maybe)
"""

_RELEASE_INSIDE_THE_CHAIN = """
from mediator_chain.clearance import Decision, clear, inspect_goods, release
from mediator_chain.domain import CustomsDeclaration


def run(declaration: CustomsDeclaration) -> Decision:
    return clear(declaration, (release, inspect_goods))
"""

_WRONG_RETURN_TYPE = """
from mediator_chain.clearance import Decision, clear
from mediator_chain.domain import CustomsDeclaration


def label(declaration: CustomsDeclaration, /) -> str:
    return "held"


def run(declaration: CustomsDeclaration) -> Decision:
    return clear(declaration, (label,))
"""

_FALLS_OFF_THE_END = """
from mediator_chain.clearance import Decision, Held
from mediator_chain.domain import CustomsDeclaration


def stage(declaration: CustomsDeclaration, /) -> Decision | None:
    if not declaration.duty_paid:
        return Held("duty unpaid")
"""

_DECISION_LEFT_UNHANDLED = """
from typing import assert_never

from mediator_chain.clearance import Decision, Released


def label(decision: Decision, /) -> str:
    match decision:
        case Released():
            return "released"
        case _:
            assert_never(decision)
"""

# Reduced model: a linked chain whose handler returns None off the end, and `describe` from src.
_LINKED_RESULT = """
from mediator_chain.clearance import ClearanceStage, Decision, describe
from mediator_chain.domain import CustomsDeclaration


class Handler:
    def __init__(self, stage: ClearanceStage, next_handler: "Handler | None" = None) -> None:
        self._stage = stage
        self._next = next_handler

    def handle(self, declaration: CustomsDeclaration, /) -> Decision | None:
        if (decision := self._stage(declaration)) is not None:
            return decision
        return self._next.handle(declaration) if self._next is not None else None


def run(chain: Handler, declaration: CustomsDeclaration) -> str:
    return describe(chain.handle(declaration))
"""

_UNKNOWN_MESSAGE = """
from mediator_chain.domain import ConsignmentId, HandlingEvent, HandlingKind
from mediator_chain.mediator import ClearanceMediator


def run(mediator: ClearanceMediator) -> None:
    mediator.receive(HandlingEvent(ConsignmentId("CN-1"), HandlingKind.LOADED, "NLRTM"))
"""

# Reduced model: a class with a bool field, matched on True and False and then on nothing.
_BOOL_PATTERNS = """
from dataclasses import dataclass
from typing import assert_never


@dataclass(frozen=True, slots=True)
class Inspection:
    passed: bool


def label(message: Inspection, /) -> str:
    match message:
        case Inspection(passed=True):
            return "passed"
        case Inspection(passed=False):
            return "failed"
        case _:
            assert_never(message)
"""


def test_mypy_refuses_a_stage_that_can_pass_as_the_final_stage(tmp_path: Path) -> None:
    stdout, status = _run(_STAGE_THAT_CAN_PASS_AS_FINAL, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'Argument "final" to "clear"' in stdout


def test_mypy_cannot_see_release_placed_inside_the_chain(tmp_path: Path) -> None:
    stdout, status = _run(_RELEASE_INSIDE_THE_CHAIN, tmp_path)

    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""


def test_mypy_refuses_a_stage_with_the_wrong_return_type(tmp_path: Path) -> None:
    stdout, status = _run(_WRONG_RETURN_TYPE, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'Argument 2 to "clear"' in stdout


def test_mypy_reports_a_stage_that_falls_off_the_end(tmp_path: Path) -> None:
    stdout, status = _run(_FALLS_OFF_THE_END, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"return"}
    assert "Missing return statement" in stdout


def test_mypy_reports_a_decision_left_unhandled(tmp_path: Path) -> None:
    stdout, status = _run(_DECISION_LEFT_UNHANDLED, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'expected "Never"' in stdout


def test_mypy_refuses_a_linked_chain_result_where_a_decision_is_needed(tmp_path: Path) -> None:
    stdout, status = _run(_LINKED_RESULT, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'Argument 1 to "describe"' in stdout


def test_mypy_refuses_a_message_the_mediator_does_not_know(tmp_path: Path) -> None:
    stdout, status = _run(_UNKNOWN_MESSAGE, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'Argument 1 to "receive"' in stdout


def test_mypy_cannot_exhaust_a_match_on_true_and_false_patterns(tmp_path: Path) -> None:
    stdout, status = _run(_BOOL_PATTERNS, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'expected "Never"' in stdout
