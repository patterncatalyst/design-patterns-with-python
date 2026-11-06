import os
import re
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
    return set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE))


# The src model, type-checked only and never run: each line breaks a check against the fallback,
# except the last, which the object fallback lets through.
_AGAINST_THE_FALLBACK = """
from singledispatch_visitor.commodities import TShirt
from singledispatch_visitor.tariff import tariff_code


@tariff_code.register
def _wrong_return(commodity: TShirt) -> int:
    return 1


code: int = tariff_code(TShirt(cotton=True))
tariff_code(TShirt(cotton=True), "EU")
tariff_code(42)
"""

# Reduced model: a fallback typed as a union of the kinds.
_UNION_FALLBACK = """
from functools import singledispatch


class Coffee: ...


class Tea: ...


class Garment: ...


@singledispatch
def strict_code(commodity: Coffee | Tea | Garment) -> str:
    raise LookupError


@strict_code.register
def _number(commodity: int) -> str:
    return "none"


strict_code(1)
"""

# Reduced model: register(cls, fn) with a class that differs from the function's parameter.
_MISMATCHED_REGISTER = """
from dataclasses import dataclass
from functools import singledispatch


class Tea: ...


@dataclass
class Garment:
    cotton: bool


@singledispatch
def tariff_code(commodity: object) -> str:
    raise LookupError


def garment_code(commodity: Garment) -> str:
    return "6109.10" if commodity.cotton else "6109.90"


tariff_code.register(Tea, garment_code)
tariff_code(Tea())
"""

# Reduced model: the annotation names a class that is defined after the decorator runs.
_FORWARD_REFERENCE = """
from functools import singledispatch


@singledispatch
def tariff_code(commodity: object) -> str:
    raise LookupError


@tariff_code.register
def _(commodity: Banana) -> str:
    return "0803.90"


class Banana: ...
"""

# The src model, run too: the argument after self goes unchecked, and the call fails at run time.
_METHOD_ARGUMENT = """
from decimal import Decimal

from singledispatch_visitor.money import Money
from singledispatch_visitor.surcharges import ReeferContainer, SurchargeSchedule

schedule = SurchargeSchedule(Money(Decimal("40.00"), "EUR"), Money(Decimal("150.00"), "EUR"))
schedule.surcharge(ReeferContainer("C-2", Decimal(-18)), "three")
"""


def test_mypy_checks_calls_and_registrations_against_the_fallback(tmp_path: Path) -> None:
    stdout, status = _run(_AGAINST_THE_FALLBACK, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type", "assignment", "call-arg"}
    assert stdout.count("error:") == 3
    assert 'Argument 1 to "tariff_code"' not in stdout


def test_mypy_refuses_a_kind_outside_a_union_fallback(tmp_path: Path) -> None:
    stdout, status = _run(_UNION_FALLBACK, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"misc", "arg-type"}
    assert "must be subtype of fallback function first argument" in stdout


def test_mypy_accepts_a_registered_class_that_differs_from_the_parameter(tmp_path: Path) -> None:
    stdout, status = _run(_MISMATCHED_REGISTER, tmp_path)

    assert status == 0
    assert stdout == ""
    assert _codes(stdout) == set()
    namespace: dict[str, object] = {}
    with pytest.raises(AttributeError, match="has no attribute 'cotton'"):
        exec(_MISMATCHED_REGISTER, namespace)


def test_mypy_accepts_a_forward_reference_that_fails_at_registration(tmp_path: Path) -> None:
    stdout, status = _run(_FORWARD_REFERENCE, tmp_path)

    assert status == 0
    assert stdout == ""
    assert _codes(stdout) == set()
    namespace: dict[str, object] = {}
    with pytest.raises(TypeError) as raised:
        exec(_FORWARD_REFERENCE, namespace)
    message = re.sub(r"0x[0-9a-f]+", "0x...", str(raised.value))
    assert message == (
        "Invalid annotation for 'commodity'. "
        "ForwardRef('Banana', owner=<function _ at 0x...>) is an unresolved forward reference."
    )
    assert "Banana" not in namespace


def test_mypy_does_not_check_the_arguments_of_a_singledispatchmethod(tmp_path: Path) -> None:
    stdout, status = _run(_METHOD_ARGUMENT, tmp_path)

    assert status == 0
    assert stdout == ""
    assert _codes(stdout) == set()
    with pytest.raises(TypeError, match="can't multiply sequence"):
        exec(_METHOD_ARGUMENT, {})
