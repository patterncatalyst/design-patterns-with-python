from dataclasses import dataclass
from decimal import Decimal

import pytest
from data_model.money import Money, RateQuote


@dataclass(frozen=True, slots=True)
class _LtOnlyMoney:
    """Negative fixture: __lt__ and no total_ordering."""

    amount: Decimal

    def __lt__(self, other: _LtOnlyMoney) -> bool:
        return self.amount < other.amount


def test_total_ordering_derives_the_other_comparisons(price: Money) -> None:
    more = Money(Decimal("13.00"), "EUR")
    assert price <= price
    assert price <= more
    assert more > price
    assert more >= price
    assert not price > more
    assert "__le__" in vars(Money)
    low, high = _LtOnlyMoney(Decimal("1")), _LtOnlyMoney(Decimal("2"))
    assert high > low
    with pytest.raises(TypeError, match="'<=' not supported"):
        _ = low <= high  # type: ignore[operator]


def test_money_refuses_to_order_across_currencies(price: Money) -> None:
    dollars = Money(Decimal("1.00"), "USD")
    with pytest.raises(ValueError, match="cannot compare USD with EUR"):
        _ = dollars < price
    with pytest.raises(ValueError, match="cannot compare USD with EUR"):
        _ = dollars <= price
    with pytest.raises(TypeError):
        _ = price < 3  # type: ignore[operator]
    assert Money(Decimal("1.00"), "USD") != Money(Decimal("1.00"), "EUR")


def test_quotes_sort_by_total_but_not_by_themselves(quotes: list[RateQuote]) -> None:
    ordered = sorted(quotes, key=lambda q: q.total)
    assert [q.consignment_id for q in ordered] == ["CN-00000002", "CN-00000003", "CN-00000001"]
    with pytest.raises(
        TypeError, match="'<' not supported between instances of 'RateQuote' and 'RateQuote'"
    ):
        sorted(quotes)  # type: ignore[type-var]
