import ast
import os
import re
import subprocess
import sys
from pathlib import Path

import mypy.api
import pytest

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
    return set(re.findall(r"\[([a-z-]+)\]", stdout))


# The snippets that add a state cannot extend the union from outside, so they re-declare the
# states and the match. test_the_static_snippets_mirror_the_source holds them to states.py.
_STATES = """
from dataclasses import dataclass
from typing import assert_never

from state_machines.domain import HandlingEvent, HandlingKind, TransitionError


@dataclass(frozen=True, slots=True)
class Booked:
    origin: str


@dataclass(frozen=True, slots=True)
class Loaded:
    port: str


@dataclass(frozen=True, slots=True)
class InTransit:
    departed_from: str
    days_sailed: int = 0
    delay_days: int = 0


@dataclass(frozen=True, slots=True)
class Cleared:
    port: str


@dataclass(frozen=True, slots=True)
class Delivered:
    port: str


@dataclass(frozen=True, slots=True)
class Held:
    port: str


type ConsignmentState = Booked | Loaded | InTransit | Cleared | Delivered | Held


def apply_event(state: ConsignmentState, event: HandlingEvent) -> ConsignmentState:
    match state:
        case Booked() if event.kind is HandlingKind.LOADED:
            return Loaded(event.location)
        case Loaded() if event.kind is HandlingKind.DEPARTED:
            return InTransit(departed_from=event.location)
        case InTransit() if event.kind is HandlingKind.CLEARED:
            return Cleared(event.location)
        case Cleared() if event.kind is HandlingKind.DELIVERED:
            return Delivered(event.location)
"""

_EXPLICIT_ILLEGAL_ARM = """
        case Booked() | Loaded() | InTransit() | Cleared() | Delivered():
            raise TransitionError(event.kind.name)
        case _:
            assert_never(state)
"""

_WILDCARD_ARM = """
        case _:
            raise TransitionError(event.kind.name)
"""

_STATE_MISSING_FROM_MATCH = _STATES + _EXPLICIT_ILLEGAL_ARM
_STATE_SWALLOWED = _STATES + _WILDCARD_ARM

_ENUM_MEMBER_MISSING = """
from enum import Enum, auto
from typing import assert_never


class ConsignmentStatus(Enum):
    BOOKED = auto()
    LOADED = auto()
    IN_TRANSIT = auto()
    CLEARED = auto()
    DELIVERED = auto()
    HELD = auto()


def label(status: ConsignmentStatus) -> str:
    match status:
        case ConsignmentStatus.BOOKED | ConsignmentStatus.LOADED:
            return "origin"
        case ConsignmentStatus.IN_TRANSIT:
            return "at sea"
        case ConsignmentStatus.CLEARED | ConsignmentStatus.DELIVERED:
            return "destination"
        case _:
            assert_never(status)
"""


@pytest.mark.parametrize(
    ("snippet", "message"),
    [
        (
            _STATE_MISSING_FROM_MATCH,
            'Argument 1 to "assert_never" has incompatible type "Held"; expected "Never"',
        ),
        (
            _ENUM_MEMBER_MISSING,
            'Argument 1 to "assert_never" has incompatible type '
            '"Literal[ConsignmentStatus.HELD]"; expected "Never"',
        ),
    ],
    ids=["dataclass-union", "enum"],
)
def test_mypy_reports_a_state_missing_from_the_match(
    snippet: str, message: str, tmp_path: Path
) -> None:
    stdout, status = _run(snippet, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert message in stdout


def test_mypy_cannot_see_a_state_swallowed_by_a_wildcard(tmp_path: Path) -> None:
    stdout, status = _run(_STATE_SWALLOWED, tmp_path)
    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""


# A reduced model: two states and two kinds are enough to cover every pair.
_TUPLE_MATCH = """
from dataclasses import dataclass
from enum import Enum, auto
from typing import assert_never


class K(Enum):
    LOADED = auto()
    DEPARTED = auto()


@dataclass(frozen=True, slots=True)
class Booked:
    origin: str


@dataclass(frozen=True, slots=True)
class Loaded:
    port: str


def step(s: Booked | Loaded, k: K) -> str:
    match (s, k):
        case (Booked(), K.LOADED):
            return "loaded"
        case (Booked(), K.DEPARTED) | (Loaded(), _):
            return "refused"
        case _:
            assert_never((s, k))
"""


def test_mypy_cannot_prove_a_tuple_match_exhaustive(tmp_path: Path) -> None:
    stdout, status = _run(_TUPLE_MATCH, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'incompatible type "tuple[Booked, K]"; expected "Never"' in stdout


_TABLE_HEAD = """
from collections.abc import Mapping

from state_machines.domain import ConsignmentStatus as S
from state_machines.domain import HandlingKind as K
"""

_SWAPPED_KEY = (
    _TABLE_HEAD
    + """
table: Mapping[tuple[S, K], S] = frozendict(
    {
        (S.BOOKED, K.LOADED): S.LOADED,
        (K.DEPARTED, S.LOADED): S.IN_TRANSIT,
    }
)
"""
)

_WRONG_VALUE = (
    _TABLE_HEAD
    + """
table: Mapping[tuple[S, K], S] = frozendict(
    {
        (S.BOOKED, K.LOADED): S.LOADED,
        (S.LOADED, K.DEPARTED): K.DEPARTED,
    }
)
"""
)

_ILLEGAL_PAIR = (
    _TABLE_HEAD
    + """
table: Mapping[tuple[S, K], S] = frozendict(
    {
        (S.BOOKED, K.LOADED): S.LOADED,
        (S.DELIVERED, K.BOOKED): S.BOOKED,
    }
)
"""
)


@pytest.mark.parametrize(
    ("snippet", "status_expected", "codes"),
    [(_SWAPPED_KEY, 1, {"dict-item"}), (_WRONG_VALUE, 1, {"dict-item"}), (_ILLEGAL_PAIR, 0, set())],
    ids=["swapped-key", "wrong-value", "illegal-pair"],
)
def test_mypy_checks_table_entry_types_but_not_legality(
    snippet: str, status_expected: int, codes: set[str], tmp_path: Path
) -> None:
    stdout, status = _run(snippet, tmp_path)
    assert status == status_expected
    assert _codes(stdout) == codes
    if codes:
        assert 'expected "tuple[ConsignmentStatus, HandlingKind]"' in stdout
    else:
        assert stdout == ""


def test_a_repeated_table_key_keeps_the_last_value() -> None:
    # A string, because a dict literal with a repeated key in this file would be a ruff F601.
    literal = "{('CLEARED', 'DELIVERED'): 'first', ('CLEARED', 'DELIVERED'): 'last'}"
    table = frozendict(ast.literal_eval(literal))
    assert len(table) == 1
    assert table[("CLEARED", "DELIVERED")] == "last"


def test_assert_never_raises_even_when_asserts_are_stripped() -> None:
    code = "assert False, 'stripped'\nfrom typing import assert_never\nassert_never('x')\n"
    result = subprocess.run(
        [sys.executable, "-I", "-O", "-c", code], capture_output=True, text=True, check=False
    )
    assert result.returncode != 0
    assert "Expected code to be unreachable, but got: 'x'" in result.stderr
    assert "stripped" not in result.stderr


_OBJECT_FORM = """
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class LifecycleState(Protocol):
    def on_loaded(self) -> LifecycleState: ...
    def on_departed(self) -> LifecycleState: ...
    def amendable(self) -> bool: ...


@dataclass(frozen=True, slots=True)
class Booked:
    def on_loaded(self) -> LifecycleState:
        return Loaded()

    def on_departed(self) -> LifecycleState:
        raise ValueError("departed")

    def amendable(self) -> bool:
        return True

"""

_LOADED_WITH_AMENDABLE = """
@dataclass(frozen=True, slots=True)
class Loaded:
    def on_loaded(self) -> LifecycleState:
        raise ValueError("loaded")

    def on_departed(self) -> LifecycleState:
        raise ValueError("departed")

    def amendable(self) -> bool:
        return False
"""

_LOADED_WITHOUT_AMENDABLE = """
@dataclass(frozen=True, slots=True)
class Loaded:
    def on_loaded(self) -> LifecycleState:
        raise ValueError("loaded")

    def on_departed(self) -> LifecycleState:
        raise ValueError("departed")
"""

_UNRETURNED_STATE = """
@dataclass(frozen=True, slots=True)
class Held:
    def on_loaded(self) -> LifecycleState:
        raise ValueError("held")
"""


def test_mypy_reports_an_operation_missing_from_a_state_object(tmp_path: Path) -> None:
    stdout, status = _run(_OBJECT_FORM + _LOADED_WITHOUT_AMENDABLE, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"return-value"}
    assert 'is missing following "LifecycleState" protocol member' in stdout
    assert "amendable" in stdout


def test_mypy_accepts_a_state_object_nothing_returns(tmp_path: Path) -> None:
    complete = _OBJECT_FORM + _LOADED_WITH_AMENDABLE
    stdout, status = _run(complete, tmp_path)
    assert (status, stdout) == (0, "")
    stdout, status = _run(complete + _UNRETURNED_STATE, tmp_path)
    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""


def _class_names(tree: ast.Module) -> list[str]:
    return [node.name for node in tree.body if isinstance(node, ast.ClassDef)]


def _match_arms(tree: ast.Module, function: str) -> list[ast.match_case]:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function:
            (match,) = (stmt for stmt in node.body if isinstance(stmt, ast.Match))
            return match.cases
    raise AssertionError(f"no function {function}")


def _arm_signature(case: ast.match_case) -> str:
    return ast.unparse(case.pattern) + (" if " + ast.unparse(case.guard) if case.guard else "")


def _union(tree: ast.Module) -> str:
    (alias,) = (n for n in tree.body if isinstance(n, ast.TypeAlias))
    return ast.unparse(alias.value)


def test_the_static_snippets_mirror_the_source() -> None:
    source = ast.parse((_SRC / "state_machines" / "states.py").read_text())
    snippet = ast.parse(_STATE_MISSING_FROM_MATCH)
    # The snippet declares the source's states, field for field, and one more.
    assert set(_class_names(snippet)) == set(_class_names(source)) | {"Held"}
    twins = {n.name: n for n in source.body if isinstance(n, ast.ClassDef)}
    for node in snippet.body:
        if isinstance(node, ast.ClassDef) and node.name != "Held":
            assert ast.dump(node) == ast.dump(twins[node.name])
    assert _union(snippet) == _union(source) + " | Held"
    # The match has the source's arms in the source's order, and the guarded arms do the same.
    source_arms = _match_arms(source, "apply_event")
    snippet_arms = _match_arms(snippet, "apply_event")
    assert [_arm_signature(c) for c in snippet_arms] == [_arm_signature(c) for c in source_arms]
    for source_arm, snippet_arm in zip(source_arms[:4], snippet_arms[:4], strict=True):
        assert ast.dump(snippet_arm) == ast.dump(source_arm)
    assert ast.unparse(snippet_arms[-1].body[0]) == "assert_never(state)"
    # Both source matches end in assert_never, so a forgotten state is a mypy error in each.
    for function in ("apply_event", "status_of"):
        last = _match_arms(source, function)[-1]
        assert ast.unparse(last.pattern) == "_"
        assert ast.unparse(last.body[0]) == "assert_never(state)"
