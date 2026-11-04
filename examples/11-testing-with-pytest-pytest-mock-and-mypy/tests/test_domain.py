from decimal import Decimal

import pytest
from testing_baseline.domain import Money, Weight


@pytest.mark.parametrize(
    "kilograms",
    [
        pytest.param(0.0, id="zero"),
        pytest.param(-1.0, id="negative"),
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="infinite"),
    ],
)
def test_weight_rejects_a_mass_that_is_not_positive_and_finite(kilograms: float) -> None:
    with pytest.raises(ValueError, match="kilograms must be positive"):
        Weight(kilograms)


def test_money_orders_by_amount_within_one_currency() -> None:
    assert Money(Decimal("9.50"), "USD") < Money(Decimal("10.00"), "USD")
    assert not Money(Decimal("10.00"), "USD") < Money(Decimal("10.00"), "USD")


def test_money_refuses_to_order_across_currencies() -> None:
    with pytest.raises(ValueError, match="cannot compare EUR with USD"):
        _ = Money(Decimal("1"), "USD") < Money(Decimal("1"), "EUR")
