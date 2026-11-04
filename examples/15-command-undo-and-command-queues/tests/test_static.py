import ast
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
    return set(re.findall(r"\[([a-z-]+)\]", stdout))


_DICT_FOR_FROZENDICT = """
from command_undo.amendments import SetInstructions

notes = {"handling": "keep dry"}
command = SetInstructions(notes)
"""

_ASSIGN_INTO_FROZENDICT = """
from command_undo.domain import BookingRequest

def edit(request: BookingRequest) -> None:
    request.instructions["handling"] = "fragile"
"""

# The snippet cannot extend the union from outside, so it re-declares the amendments and apply.
# test_the_amendment_snippet_mirrors_the_source holds it to amendments.py.
_AMENDMENTS = """
import re
from dataclasses import dataclass, replace
from typing import assert_never

from command_undo.domain import AmendmentError, BookingRequest, Weight

_PORT_CODE = re.compile(r"[A-Z]{5}")


@dataclass(frozen=True, slots=True)
class Reweigh:
    weight: Weight


@dataclass(frozen=True, slots=True)
class Redirect:
    destination: str


@dataclass(frozen=True, slots=True)
class SetInstructions:
    instructions: frozendict[str, str]


@dataclass(frozen=True, slots=True)
class Insure:
    insured: bool


type Amendment = Reweigh | Redirect | SetInstructions | Insure


def apply(request: BookingRequest, amendment: Amendment) -> tuple[BookingRequest, Amendment]:
    match amendment:
        case Reweigh(weight):
            amended = replace(request, consignment=replace(request.consignment, weight=weight))
            return amended, Reweigh(request.consignment.weight)
        case Redirect(destination):
            if not _PORT_CODE.fullmatch(destination):
                raise AmendmentError(f"not a port code: {destination!r}")
            amended = replace(
                request, consignment=replace(request.consignment, destination=destination)
            )
            return amended, Redirect(request.consignment.destination)
        case SetInstructions(instructions):
            return replace(request, instructions=instructions), SetInstructions(
                request.instructions
            )
        case _:
            assert_never(amendment)
"""

_SHARED_DICT = """
from dataclasses import dataclass, replace

from command_undo.domain import Consignment


@dataclass(frozen=True, slots=True)
class LooseRequest:
    consignment: Consignment
    instructions: dict[str, str]


@dataclass(frozen=True, slots=True)
class LooseSetInstructions:
    instructions: dict[str, str]


def apply(
    request: LooseRequest, command: LooseSetInstructions
) -> tuple[LooseRequest, LooseSetInstructions]:
    return (
        replace(request, instructions=command.instructions),
        LooseSetInstructions(request.instructions),
    )


notes = {"handling": "keep dry"}
command = LooseSetInstructions(notes)
"""


def test_mypy_rejects_a_dict_where_frozen_instructions_belong(tmp_path: Path) -> None:
    stdout, status = _run(_DICT_FOR_FROZENDICT, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'expected "frozendict[str, str]"' in stdout


def test_mypy_rejects_assigning_into_frozen_instructions(tmp_path: Path) -> None:
    stdout, status = _run(_ASSIGN_INTO_FROZENDICT, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"index"}
    assert 'Unsupported target for indexed assignment ("frozendict[str, str]")' in stdout


def test_mypy_reports_an_amendment_kind_missing_from_apply(tmp_path: Path) -> None:
    stdout, status = _run(_AMENDMENTS, tmp_path)
    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'incompatible type "Insure"; expected "Never"' in stdout


def test_mypy_accepts_commands_that_share_a_dict(tmp_path: Path) -> None:
    stdout, status = _run(_SHARED_DICT, tmp_path)
    assert (status, stdout) == (0, "")


def _classes(tree: ast.Module) -> dict[str, ast.ClassDef]:
    return {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}


def _shape(node: ast.ClassDef) -> list[str]:
    """The decorators and fields of a class, without its docstring."""
    decorators = [ast.dump(d) for d in node.decorator_list]
    fields = [ast.dump(n) for n in node.body if isinstance(n, ast.AnnAssign)]
    return decorators + fields


def _apply(tree: ast.Module) -> ast.FunctionDef:
    (function,) = (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "apply")
    return function


def _union(tree: ast.Module) -> str:
    (alias,) = (n for n in tree.body if isinstance(n, ast.TypeAlias))
    return ast.unparse(alias.value)


def _arms(tree: ast.Module) -> list[ast.match_case]:
    (match,) = (stmt for stmt in _apply(tree).body if isinstance(stmt, ast.Match))
    return match.cases


def test_the_amendment_snippet_mirrors_the_source() -> None:
    source = ast.parse((_SRC / "command_undo" / "amendments.py").read_text())
    snippet = ast.parse(_AMENDMENTS)
    twins = _classes(source)
    assert set(_classes(snippet)) == set(twins) | {"Insure"}
    for name, node in _classes(snippet).items():
        if name != "Insure":
            assert _shape(node) == _shape(twins[name])
    assert _union(snippet) == _union(source) + " | Insure"
    source_arms, snippet_arms = _arms(source), _arms(snippet)
    assert len(snippet_arms) == len(source_arms)
    for source_arm, snippet_arm in zip(source_arms[:-1], snippet_arms[:-1], strict=True):
        assert ast.dump(snippet_arm) == ast.dump(source_arm)


def test_apply_ends_in_assert_never() -> None:
    for text in ((_SRC / "command_undo" / "amendments.py").read_text(), _AMENDMENTS):
        last = _arms(ast.parse(text))[-1]
        assert ast.unparse(last.pattern) == "_"
        assert ast.unparse(last.body[0]) == "assert_never(amendment)"
