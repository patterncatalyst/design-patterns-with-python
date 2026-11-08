import os
import re
from decimal import Decimal
from pathlib import Path

import mypy.api
import pytest
from seams import legacy
from seams.domain import Consignment

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


# A replacement that takes one parameter where the carrier call passes two.
_WRONG_REPLACEMENT = """
from decimal import Decimal

import pytest
from seams import legacy


def wrong(zone: str) -> Decimal:
    return Decimal("1")


def patch_it(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(legacy, "request_quote", wrong)
"""

_ASSIGN_WRONG = """
from decimal import Decimal

from seams import legacy


def wrong(zone: str) -> Decimal:
    return Decimal("1")


legacy.request_quote = wrong
"""

_REVEAL_PATCH = """
from decimal import Decimal
from unittest.mock import patch


def replacement(zone: str, weight_kg: Decimal) -> Decimal:
    return Decimal("1")


with patch("seams.legacy.request_quote") as first:
    reveal_type(first)

with patch("seams.legacy.request_quote", new=replacement) as second:
    reveal_type(second)
"""

_DECORATOR_UNANNOTATED = """
from unittest.mock import patch


@patch("seams.legacy.request_quote")
def check(replaced) -> None:
    replaced.return_value = None
"""

_DECORATOR_ANNOTATED = """
from unittest.mock import MagicMock, patch


@patch("seams.legacy.request_quote")
def check(replaced: MagicMock) -> None:
    replaced.return_value = None
"""

# Reduced model: a callback Protocol stands for the parameter a refactored engine would take.
_PROTOCOL_PARAMETER = """
from decimal import Decimal
from typing import Protocol


class FastlineQuote(Protocol):
    def __call__(self, zone: str, weight_kg: Decimal, /) -> Decimal: ...


def engine(fastline_quote: FastlineQuote) -> Decimal:
    return fastline_quote("EU", Decimal("12.5"))


def one_parameter(zone: str) -> Decimal:
    return Decimal("1")


engine(one_parameter)
"""

_MISSPELT_TARGET = """
from decimal import Decimal

import pytest


def fake(zone: str, weight_kg: Decimal) -> Decimal:
    return Decimal("1")


def patch_it(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("seams.legacy.request_qoute", fake)
"""


def test_mypy_does_not_check_a_monkeypatched_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, consignment: Consignment
) -> None:
    stdout, status = _run(_WRONG_REPLACEMENT, tmp_path)

    assert status == 0, stdout
    assert _codes(stdout) == []

    def wrong(zone: str) -> Decimal:
        return Decimal("1")

    monkeypatch.setattr(legacy, "request_quote", wrong)
    with pytest.raises(TypeError, match="positional argument"):
        legacy.RateEngine().quote(consignment)


def test_mypy_checks_a_direct_assignment_to_a_module_name(tmp_path: Path) -> None:
    stdout, status = _run(_ASSIGN_WRONG, tmp_path)

    assert status == 1
    # The name is also not re-exported by seams.legacy, which mypy --strict reports separately.
    assert _codes(stdout) == ["assignment", "attr-defined"]
    assert (
        'error: Module "seams.legacy" does not explicitly export attribute "request_quote"'
        "  [attr-defined]"
    ) in stdout
    assert (
        'error: Incompatible types in assignment (expression has type "Callable[[str], Decimal]", '
        'variable has type "Callable[[str, Decimal], Decimal]")  [assignment]'
    ) in stdout


def test_mypy_types_a_patch_as_a_magic_mock_or_as_its_replacement(tmp_path: Path) -> None:
    stdout, status = _run(_REVEAL_PATCH, tmp_path)

    assert status == 0, stdout
    assert 'Revealed type is "unittest.mock.MagicMock | unittest.mock.AsyncMock"' in stdout
    assert (
        'Revealed type is "def (zone: str, weight_kg: decimal.Decimal) -> decimal.Decimal"'
    ) in stdout


def test_mypy_requires_an_annotation_on_a_decorator_injected_mock(tmp_path: Path) -> None:
    stdout, status = _run(_DECORATOR_UNANNOTATED, tmp_path)
    annotated_stdout, annotated_status = _run(_DECORATOR_ANNOTATED, tmp_path)

    assert status == 1
    assert _codes(stdout) == ["no-untyped-def"]
    assert annotated_status == 0, annotated_stdout
    assert _codes(annotated_stdout) == []


def test_mypy_checks_a_fake_passed_to_a_protocol_parameter(tmp_path: Path) -> None:
    stdout, status = _run(_PROTOCOL_PARAMETER, tmp_path)

    assert status == 1
    assert _codes(stdout) == ["arg-type"]
    assert "FastlineQuote" in stdout


def test_mypy_accepts_a_misspelt_monkeypatch_target_string(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stdout, status = _run(_MISSPELT_TARGET, tmp_path)

    assert status == 0, stdout
    assert _codes(stdout) == []

    def fake(zone: str, weight_kg: Decimal) -> Decimal:
        return Decimal("1")

    with pytest.raises(AttributeError, match="has no attribute 'request_qoute'"):
        monkeypatch.setattr("seams.legacy.request_qoute", fake)
