"""Fixtures: a first draft of the rewrite, an engine that must not be called, a consignment builder.

The first draft is the rewrite written with ``bisect_right``. It lives here, not in ``src``,
because it is the mistake the parity table exists to catch.
"""

from bisect import bisect_right
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

import pytest
from refactor_or_rewrite.domain import (
    MARGIN,
    Consignment,
    ConsignmentId,
    Money,
    RateQuote,
    RatingError,
    Weight,
)
from refactor_or_rewrite.rating import STANDARD_TARIFF

if TYPE_CHECKING:
    from collections.abc import Callable

    from refactor_or_rewrite.rating import Tariff


def _exclusive_limits_quote(
    consignment: Consignment, /, *, tariff: Tariff = STANDARD_TARIFF
) -> RateQuote:
    """The rewrite as first drafted: a weight equal to a limit leaves the band that limit closes."""
    try:
        band_prices = tariff.prices[consignment.zone]
    except KeyError:
        raise RatingError(f"no tariff for zone {consignment.zone!r}") from None
    kg = consignment.weight.kilograms
    band = bisect_right(tariff.upper_kg, kg)
    if band == len(tariff.upper_kg):
        raise RatingError(f"no band for {kg} kg")
    total = (band_prices[band] * MARGIN).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return RateQuote(consignment.id, Money(total))


def _refusing_quoter(consignment: Consignment, /) -> RateQuote:
    raise RatingError("engine not expected to be called")


@pytest.fixture
def first_draft() -> Callable[[Consignment], RateQuote]:
    return _exclusive_limits_quote


@pytest.fixture
def refusing_quoter() -> Callable[[Consignment], RateQuote]:
    return _refusing_quoter


@pytest.fixture
def consignment_for() -> Callable[[str, str], Consignment]:
    def build(zone: str, kilograms: str) -> Consignment:
        return Consignment(ConsignmentId("CN-1"), zone, Weight(Decimal(kilograms)))

    return build
