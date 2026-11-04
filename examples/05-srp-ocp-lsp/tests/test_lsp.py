import os
import re
from decimal import Decimal
from pathlib import Path

import mypy.api
import pytest
from srp_ocp_lsp.domain import Consignment, ConsignmentId, Money, RatingError, Weight
from srp_ocp_lsp.pricing import FLAT_BY_ZONE, TARIFF, ZONES, BaseRate, FlatRate, RateCalculator

_SRC = Path(__file__).resolve().parents[1] / "src"


def assert_rate_contract(calculator: RateCalculator, *, currency: str = "EUR") -> None:
    """Check the behavioural half of the RateCalculator contract, which no type states."""
    for zone in ZONES:
        prices: list[Money] = []
        for kilograms in (0.5, 1200.0):
            consignment = Consignment(
                id=ConsignmentId("CN-CONTRACT"),
                weight=Weight(kilograms),
                zone=zone,
                destination="NLRTM",
            )
            try:
                price = calculator.price(consignment)
            except RatingError:
                raise AssertionError(f"rejected zone {zone} that the contract accepts") from None
            if price.currency != currency:
                raise AssertionError(f"priced in {price.currency}, contract requires {currency}")
            assert price.amount >= 0
            assert price.amount == price.amount.quantize(Decimal("0.01"))
            prices.append(price)
        assert prices[0].amount <= prices[1].amount


class AsiaOnlyRate(BaseRate):
    """Negative fixture: strengthens the precondition by rejecting zones the contract accepts."""

    def price(self, consignment: Consignment, /) -> Money:
        if consignment.zone != "ASIA":
            raise RatingError(f"only ASIA is served, got {consignment.zone!r}")
        return super().price(consignment)


class DollarRate:
    """Negative fixture: structural, and weakens the postcondition by pricing in USD."""

    def price(self, consignment: Consignment, /) -> Money:
        return Money(Decimal("10.00"), "USD")


@pytest.mark.parametrize(
    "calculator", [BaseRate(TARIFF), FlatRate(FLAT_BY_ZONE)], ids=["BaseRate", "FlatRate"]
)
def test_calculator_honours_the_rate_contract(calculator: RateCalculator) -> None:
    assert_rate_contract(calculator)


def test_contract_catches_a_strengthened_precondition() -> None:
    with pytest.raises(AssertionError, match="rejected zone EU"):
        assert_rate_contract(AsiaOnlyRate(TARIFF))


def test_contract_catches_a_weakened_postcondition() -> None:
    with pytest.raises(AssertionError, match="priced in USD"):
        assert_rate_contract(DollarRate())


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


_HEADER = """
from decimal import Decimal
from typing import override

from srp_ocp_lsp.domain import Consignment, ConsignmentId, Money
from srp_ocp_lsp.pricing import BaseRate
"""

_NARROWED_ARGUMENT = (
    _HEADER
    + """

class Narrowed(BaseRate):
    @override
    def price(self, consignment_id: ConsignmentId, /) -> Money:
        return Money(Decimal("0.00"), "EUR")
"""
)

_WIDENED_RETURN = (
    _HEADER
    + """

class WidenedReturn(BaseRate):
    @override
    def price(self, consignment: Consignment, /) -> Money | None:
        return Money(Decimal("0.00"), "EUR")
"""
)

_MISSPELLED = (
    _HEADER
    + """

class Misspelled(BaseRate):
    @override
    def prcie(self, consignment: Consignment, /) -> Money:
        return Money(Decimal("0.00"), "EUR")
"""
)

_WIDENED_ARGUMENT = (
    _HEADER
    + """

class WidenedArgument(BaseRate):
    @override
    def price(self, consignment: Consignment | None, /) -> Money:
        return Money(Decimal("0.00"), "EUR")
"""
)

_STRUCTURAL = """
from decimal import Decimal

from srp_ocp_lsp.audit import AuditSink
from srp_ocp_lsp.domain import Consignment, RateQuote
from srp_ocp_lsp.rating import quote
from srp_ocp_lsp.tax import TAX_RULES


class DecimalRate:
    def price(self, consignment: Consignment, /) -> Decimal:
        return Decimal("0.00")


def rate(consignment: Consignment, audit: AuditSink) -> RateQuote:
    return quote(consignment, calculator=DecimalRate(), tax_rules=TAX_RULES, audit=audit)
"""

_BEHAVIOURAL = """
from decimal import Decimal

from srp_ocp_lsp.audit import AuditSink
from srp_ocp_lsp.domain import Consignment, Money, RateQuote, RatingError
from srp_ocp_lsp.pricing import TARIFF, BaseRate
from srp_ocp_lsp.rating import quote
from srp_ocp_lsp.tax import TAX_RULES


class AsiaOnlyRate(BaseRate):
    def price(self, consignment: Consignment, /) -> Money:
        if consignment.zone != "ASIA":
            raise RatingError("only ASIA is served")
        return super().price(consignment)


class DollarRate:
    def price(self, consignment: Consignment, /) -> Money:
        return Money(Decimal("10.00"), "USD")


def rate(consignment: Consignment, audit: AuditSink) -> list[RateQuote]:
    return [
        quote(consignment, calculator=AsiaOnlyRate(TARIFF), tax_rules=TAX_RULES, audit=audit),
        quote(consignment, calculator=DollarRate(), tax_rules=TAX_RULES, audit=audit),
    ]
"""


@pytest.mark.parametrize(
    ("snippet", "code", "message"),
    [
        (_NARROWED_ARGUMENT, "override", "This violates the Liskov substitution principle"),
        (_WIDENED_RETURN, "override", 'Return type "Money | None"'),
        (_MISSPELLED, "misc", "marked as an override, but no base method was found"),
    ],
    ids=["narrowed-argument", "widened-return", "misspelled-override"],
)
def test_mypy_rejects_an_incompatible_override(
    snippet: str, code: str, message: str, tmp_path: Path
) -> None:
    stdout, status = _run(snippet, tmp_path)

    assert status == 1
    assert _codes(stdout) == {code}
    assert message in stdout


def test_mypy_accepts_an_override_that_widens_the_argument(tmp_path: Path) -> None:
    stdout, status = _run(_WIDENED_ARGUMENT, tmp_path)

    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""


def test_mypy_checks_a_structural_calculator_where_it_is_used(tmp_path: Path) -> None:
    stdout, status = _run(_STRUCTURAL, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert "Following member(s)" in stdout


def test_mypy_cannot_see_a_behavioural_violation(tmp_path: Path) -> None:
    stdout, status = _run(_BEHAVIOURAL, tmp_path)

    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""
