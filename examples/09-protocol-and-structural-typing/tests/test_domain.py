from decimal import Decimal

import pytest
from structural_typing.domain import Money, Weight


@pytest.mark.parametrize("kilograms", [0.0, -1.0, float("inf"), float("nan")])
def test_weight_must_be_positive_and_finite(kilograms: float) -> None:
    with pytest.raises(ValueError, match="kilograms must be positive and finite"):
        Weight(kilograms)


def test_money_addition_needs_one_currency() -> None:
    assert Money(Decimal("1.00"), "EUR") + Money(Decimal("2.00"), "EUR") == Money(
        Decimal("3.00"), "EUR"
    )
    with pytest.raises(ValueError, match="cannot add USD to EUR"):
        Money(Decimal("1.00"), "EUR") + Money(Decimal("2.00"), "USD")
