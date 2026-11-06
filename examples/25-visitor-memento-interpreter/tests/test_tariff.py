from collections.abc import Callable
from decimal import Decimal

import pytest
from visitor_memento_interpreter.domain import Consignment, Money, Weight
from visitor_memento_interpreter.tariff import (
    STANDARD_TARIFF,
    Add,
    Expr,
    Flat,
    Max,
    OverWeight,
    PerKg,
    evaluate,
    explain,
)

type PricingRule = Callable[[Consignment], Money]


def _eur(amount: str) -> Money:
    return Money(Decimal(amount), "EUR")


@pytest.mark.parametrize(
    ("kilograms", "price"),
    [
        pytest.param("10", "45.00", id="10"),
        pytest.param("100", "120.00", id="100"),
        pytest.param("100.333", "120.40", id="100.333"),
        pytest.param("1000", "1200.00", id="1000"),
        pytest.param("2000", "2225.00", id="2000"),
    ],
)
def test_every_rule_form_prices_the_same_consignments(
    rule_form: PricingRule,
    consignment: Callable[[str], Consignment],
    kilograms: str,
    price: str,
) -> None:
    assert rule_form(consignment(kilograms)) == _eur(price)


def test_explain_writes_the_tariff_as_text() -> None:
    assert explain(STANDARD_TARIFF) == (
        "over 1000 kg: 1.10 EUR per kg + 25.00 EUR; "
        "otherwise the larger of 1.20 EUR per kg and 45.00 EUR"
    )


def test_equal_tariff_trees_compare_and_hash_equal() -> None:
    same: Expr = OverWeight(
        Decimal(1000),
        Add(PerKg(_eur("1.10")), Flat(_eur("25.00"))),
        Max(PerKg(_eur("1.20")), Flat(_eur("45.00"))),
    )
    other: Expr = OverWeight(
        Decimal(1000),
        Add(PerKg(_eur("1.10")), Flat(_eur("25.00"))),
        Max(PerKg(_eur("1.30")), Flat(_eur("45.00"))),
    )

    assert same == STANDARD_TARIFF
    assert hash(same) == hash(STANDARD_TARIFF)
    assert other != STANDARD_TARIFF


def test_closures_built_the_same_way_are_not_equal(
    build_closure_tariff: Callable[[], PricingRule],
) -> None:
    first = build_closure_tariff()

    assert first == first
    assert first != build_closure_tariff()


def test_a_rule_in_another_currency_is_refused(consignment: Callable[[str], Consignment]) -> None:
    mixed = Add(PerKg(_eur("1.00")), Flat(Money(Decimal("5.00"), "USD")))

    with pytest.raises(ValueError, match="cannot add USD to EUR"):
        evaluate(mixed, consignment("10"))


def test_the_larger_of_two_rules_in_different_currencies_is_refused(
    consignment: Callable[[str], Consignment],
) -> None:
    mixed = Max(PerKg(_eur("1.00")), Flat(Money(Decimal("5.00"), "USD")))

    with pytest.raises(ValueError, match="cannot compare USD with EUR"):
        evaluate(mixed, consignment("10"))


@pytest.mark.parametrize("kilograms", ["0", "-1", "NaN", "Infinity"])
def test_a_weight_must_be_positive_and_finite_for_a_priced_consignment(kilograms: str) -> None:
    with pytest.raises(ValueError, match="positive and finite"):
        Weight(Decimal(kilograms))
