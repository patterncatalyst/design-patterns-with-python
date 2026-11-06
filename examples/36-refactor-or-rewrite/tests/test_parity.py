"""Parity: the rewrite must match the legacy engine except where a difference is recorded."""

from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from refactor_or_rewrite.domain import Consignment, ConsignmentId, RateQuote, RatingError, Weight
from refactor_or_rewrite.legacy import RateEngine
from refactor_or_rewrite.rating import Tariff, quote

if TYPE_CHECKING:
    type Quoter = Callable[[Consignment], RateQuote]

# Weights sit either side of every limit (5, 20, 50 kg), on it, and well above the last band.
_WEIGHTS = ("0.5", "5", "5.001", "20", "20.5", "50", "50.001", "60")
PARITY_ROWS = [(zone, kg) for zone in ("EU", "ASIA") for kg in _WEIGHTS] + [("AFRICA", "5")]

# The rewrite refuses an unknown zone; the legacy engine prices it as EU. That was decided.
ACCEPTED_DIFFERENCES = ["AFRICA-5"]


def _outcome(engine: Quoter, zone: str, kilograms: str) -> str:
    """The quoted amount, or the refusal, as text."""
    consignment = Consignment(ConsignmentId("CN-1"), zone, Weight(Decimal(kilograms)))
    try:
        return str(engine(consignment).total.amount)
    except RatingError as error:
        return f"RatingError: {error}"


def _mismatches(rewrite: Quoter) -> list[str]:
    """The ids of the rows where the rewrite and the legacy engine disagree, in table order."""
    legacy = RateEngine().quote
    return [
        f"{zone}-{kg}"
        for zone, kg in PARITY_ROWS
        if _outcome(legacy, zone, kg) != _outcome(rewrite, zone, kg)
    ]


def test_the_rewrite_differs_from_the_legacy_engine_only_where_accepted() -> None:
    assert _mismatches(quote) == ACCEPTED_DIFFERENCES


def test_a_first_draft_with_exclusive_band_limits_fails_parity_at_the_boundaries(
    first_draft: Quoter,
) -> None:
    assert _mismatches(first_draft) == [
        "EU-5",
        "EU-20",
        "EU-50",
        "ASIA-5",
        "ASIA-20",
        "ASIA-50",
        "AFRICA-5",
    ]


def test_the_legacy_engine_prices_an_unknown_zone_as_eu() -> None:
    legacy = RateEngine().quote

    assert [_outcome(legacy, "AFRICA", "5"), _outcome(legacy, "EU", "5")] == ["13.20", "13.20"]


def test_the_rewrite_refuses_an_unknown_zone(
    consignment_for: Callable[[str, str], Consignment],
) -> None:
    with pytest.raises(RatingError, match=r"no tariff for zone 'AFRICA'"):
        quote(consignment_for("AFRICA", "5"))


@pytest.mark.parametrize("engine", [RateEngine().quote, quote], ids=["legacy", "rewrite"])
def test_band_limits_include_the_boundary_weight(engine: Quoter) -> None:
    assert [_outcome(engine, "EU", "5"), _outcome(engine, "EU", "5.001")] == ["13.20", "27.50"]


@pytest.mark.parametrize("kilograms", ["0", "-1", "NaN", "Infinity"])
def test_a_weight_must_be_positive_and_finite(kilograms: str) -> None:
    with pytest.raises(ValueError, match="kilograms must be positive and finite"):
        Weight(Decimal(kilograms))


def test_the_rewrite_prices_from_the_tariff_it_is_given_and_rounds_half_up(
    consignment_for: Callable[[str, str], Consignment],
) -> None:
    # 0.15 plus the margin is 0.165: a half cent, so half-up gives 0.17 where half-even gives 0.16.
    tariff = Tariff(upper_kg=(Decimal(10),), prices={"EU": (Decimal("0.15"),)})

    assert str(quote(consignment_for("EU", "1"), tariff=tariff).total.amount) == "0.17"
