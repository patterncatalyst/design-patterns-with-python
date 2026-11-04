from decimal import Decimal

import pytest
from data_model.money import Money


def test_money_adds_within_one_currency_only(price: Money) -> None:
    assert price + Money(Decimal("0.75"), "EUR") == Money(Decimal("13.25"), "EUR")
    with pytest.raises(ValueError, match="cannot add USD to EUR"):
        price + Money(Decimal("1.00"), "USD")
    with pytest.raises(TypeError, match="'Money' and 'int'"):
        price + 1  # type: ignore[operator]
    with pytest.raises(TypeError, match="'int' and 'Money'"):
        1 + price  # type: ignore[operator]


def test_a_factor_times_money_uses_the_reflected_method(price: Money) -> None:
    assert Decimal("2") * price == Money(Decimal("25.00"), "EUR")
    assert 2 * price == Money(Decimal("25.00"), "EUR")
    assert price * Decimal("0.333") == Money(Decimal("4.16"), "EUR")
    with pytest.raises(TypeError, match="'Money' and 'float'"):
        _ = price * 1.5  # type: ignore[operator]
    with pytest.raises(TypeError, match="'float' and 'Money'"):
        _ = 1.5 * price  # type: ignore[operator]


def test_money_multiplication_rounds_half_up() -> None:
    assert Money(Decimal("0.10"), "EUR") * Decimal("0.25") == Money(Decimal("0.03"), "EUR")
    assert Money(Decimal("0.30"), "EUR") * Decimal("0.25") == Money(Decimal("0.08"), "EUR")


def test_sum_needs_a_money_start(price: Money) -> None:
    prices = [price, price, price]
    assert sum(prices, start=Money(Decimal("0.00"), "EUR")) == Money(Decimal("37.50"), "EUR")
    with pytest.raises(TypeError, match="'int' and 'Money'"):
        sum(prices)  # type: ignore[arg-type]
