from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

import pytest
from strategy_callable.domain import Consignment, ConsignmentId, Money, RatingError, Weight
from strategy_callable.rules import RATE_RULES, TARIFF, Tariff, ZoneRate


def _at(kilograms: str, zone: str) -> Consignment:
    return Consignment(
        id=ConsignmentId("CN-00000004"),
        weight=Weight(Decimal(kilograms)),
        zone=zone,
        destination="NLRTM",
    )


@pytest.mark.parametrize(
    ("key", "kilograms", "rate", "half_up", "half_even"),
    [
        pytest.param("per-kg", "0.1875", "1.20", "0.23", "0.22", id="per-kg"),
        pytest.param("zone", "28.85", "0.50", "14.43", "14.42", id="zone"),
    ],
)
def test_rules_round_half_up_to_cents(
    key: str, kilograms: str, rate: str, half_up: str, half_even: str
) -> None:
    exact = Decimal(kilograms) * Decimal(rate)
    # The case sits on a half cent, so the two rounding modes disagree.
    assert exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) == Decimal(half_up)
    assert exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN) == Decimal(half_even)
    assert RATE_RULES[key](_at(kilograms, "EU")) == Money(Decimal(half_up), "EUR")
    assert str(RATE_RULES[key](_at(kilograms, "EU")).amount) == half_up


def test_zone_rate_refuses_a_zone_without_a_tariff() -> None:
    with pytest.raises(RatingError, match="no tariff for zone 'MARS'") as raised:
        ZoneRate(TARIFF)(_at("10", "MARS"))
    assert raised.value.__suppress_context__
    assert ZoneRate(Tariff(frozendict({"MARS": Decimal("9")})))(_at("1", "MARS")) == Money(
        Decimal("9.00"), "EUR"
    )


@pytest.mark.parametrize("kilograms", ["0", "-1", "NaN", "Infinity"])
def test_a_rated_weight_must_be_positive_and_finite(kilograms: str) -> None:
    with pytest.raises(ValueError, match="positive and finite"):
        Weight(Decimal(kilograms))
