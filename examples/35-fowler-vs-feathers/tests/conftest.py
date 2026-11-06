"""Fixtures: the rate cards, four forms of the engine and the option that rewrites the golden file.

The rate cards stand in for the two carriers over the whole grid. The forms are the legacy engine,
the refactored engine and two refactors that change a total by a cent; each is built from the same
two plain functions.
"""

from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING, override

import pytest
from fowler_feathers import legacy, refactored
from fowler_feathers.domain import Money
from fowler_feathers.refactored import CENT

if TYPE_CHECKING:
    from fowler_feathers.domain import Consignment, RateQuote
    from fowler_feathers.legacy import AircoPrice, FastlineQuote

type QuoteFor = Callable[[Consignment], RateQuote]
type Form = Callable[[FastlineQuote, AircoPrice], QuoteFor]

_FASTLINE_CARDS = {
    "EU": (Decimal("4.20"), Decimal("0.845")),
    "ASIA": (Decimal("9.50"), Decimal("1.315")),
}
_AIRCO_CARDS = {"EU": (300, 48), "ASIA": (800, 70)}
_AIRCO_STEP_GRAMS = 500


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="rewrite tests/golden/rate_quotes.json from the legacy engine",
    )


def _fastline_card(zone: str, weight_kg: Decimal) -> Decimal:
    """FASTLINE: a base price plus a price per kilogram, at full precision."""
    base, per_kg = _FASTLINE_CARDS[zone]
    return base + per_kg * weight_kg


def _airco_card(*, destination: str, grams: int) -> int:
    """AIRCO: a fixed price plus a step for every started 500 g, in cents."""
    fixed, step = _AIRCO_CARDS[destination]
    return fixed + step * -(-grams // _AIRCO_STEP_GRAMS)


class _CentFirstRateEngine(refactored.RateEngine):
    """A refactor: Replace Primitive with Object, with a Money rounded when it is made."""

    @override
    def _prices(self, consignment: Consignment) -> dict[str, Money]:
        prices = super()._prices(consignment)
        return {
            code: Money(price.amount.quantize(CENT, rounding=ROUND_HALF_UP))
            for code, price in prices.items()
        }


class _RoundBuiltinRateEngine(refactored.RateEngine):
    """A refactor: Substitute Algorithm, with round(amount, 2) for the half-up quantise."""

    @override
    def _with_margin(self, price: Money) -> Money:
        return Money(round(price.amount * self._margin, 2), price.currency)


def _form(engine_class: type[legacy.RateEngine] | type[refactored.RateEngine]) -> Form:
    def build(fastline: FastlineQuote, airco: AircoPrice) -> QuoteFor:
        return engine_class(fastline_quote=fastline, airco_price=airco).quote

    return build


@pytest.fixture
def engine_forms() -> dict[str, Form]:
    """Each form of the engine, built from a FASTLINE function and an AIRCO function."""
    return {
        "legacy": _form(legacy.RateEngine),
        "refactored": _form(refactored.RateEngine),
        "cent-first": _form(_CentFirstRateEngine),
        "round-builtin": _form(_RoundBuiltinRateEngine),
    }


@pytest.fixture
def rate_cards() -> tuple[FastlineQuote, AircoPrice]:
    """The test rate cards: what the two carriers charge for any zone and weight in the grid."""
    return _fastline_card, _airco_card
