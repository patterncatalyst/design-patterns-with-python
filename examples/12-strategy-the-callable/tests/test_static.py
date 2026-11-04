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
    return set(re.findall(r"\[([a-z-]+)\]", stdout))


_REGISTRY_HEAD = """
from collections.abc import Mapping
from decimal import Decimal
from functools import partial

from strategy_callable.domain import Consignment, Money
from strategy_callable.rules import TARIFF, PricingRule, ZoneRate, flat_rate, per_kg
"""

_VALID = (
    _REGISTRY_HEAD
    + """
rules: Mapping[str, PricingRule] = frozendict(
    {
        "flat": flat_rate,
        "per-kg": partial(per_kg, rate=Decimal("1.20")),
        "zone": ZoneRate(TARIFF),
    }
)
"""
)

_WRONG_RETURN = (
    _REGISTRY_HEAD
    + """
def decimal_rule(consignment: Consignment) -> Decimal:
    return Decimal(1)


rules: Mapping[str, PricingRule] = frozendict({"flat": decimal_rule})
"""
)

_EXTRA_PARAMETER = (
    _REGISTRY_HEAD
    + """
rules: Mapping[str, PricingRule] = frozendict({"per-kg": per_kg})
"""
)

_LAMBDA_BODY = (
    _REGISTRY_HEAD
    + """
rules: Mapping[str, PricingRule] = frozendict({"flat": lambda c: Decimal(1)})
"""
)

_CLASS_NOT_INSTANCE = (
    _REGISTRY_HEAD
    + """
rules: Mapping[str, PricingRule] = frozendict({"zone": ZoneRate})
"""
)

_ENTRY = 'expected "str": "Callable[[Consignment], Money]"'


@pytest.mark.parametrize(
    ("snippet", "status", "codes", "messages"),
    [
        (_VALID, 0, set(), []),
        (_WRONG_RETURN, 1, {"dict-item"}, [_ENTRY, '"Callable[[Consignment], Decimal]"']),
        (
            _EXTRA_PARAMETER,
            1,
            {"dict-item"},
            [_ENTRY, "def per_kg(consignment: Consignment, *, rate: Decimal) -> Money"],
        ),
        (_LAMBDA_BODY, 1, {"dict-item", "return-value"}, [_ENTRY]),
        (_CLASS_NOT_INSTANCE, 1, {"dict-item"}, [_ENTRY, '"type[ZoneRate]"']),
    ],
    ids=["valid", "wrong-return", "extra-parameter", "lambda-body", "class-not-instance"],
)
def test_mypy_checks_each_registry_entry(
    snippet: str, status: int, codes: set[str], messages: list[str], tmp_path: Path
) -> None:
    stdout, actual = _run(snippet, tmp_path)
    assert actual == status
    assert _codes(stdout) == codes
    if not status:
        assert stdout == ""
    for message in messages:
        assert message in stdout


_UNBOUND = (
    _REGISTRY_HEAD
    + """
rules: Mapping[str, PricingRule] = frozendict({"per-kg": partial(per_kg)})
"""
)

_MISSPELT = (
    _REGISTRY_HEAD
    + """
rules: Mapping[str, PricingRule] = frozendict({"per-kg": partial(per_kg, rat=Decimal("1.20"))})
"""
)


@pytest.mark.parametrize(
    ("snippet", "status", "codes"),
    [(_UNBOUND, 0, set()), (_MISSPELT, 1, {"call-arg"})],
    ids=["missing", "misspelt"],
)
def test_mypy_checks_partial_keywords_but_not_a_missing_binding(
    snippet: str, status: int, codes: set[str], tmp_path: Path
) -> None:
    stdout, actual = _run(snippet, tmp_path)
    assert actual == status
    assert _codes(stdout) == codes
    if status:
        assert 'did you mean "rate"' in stdout
    else:
        assert stdout == ""
