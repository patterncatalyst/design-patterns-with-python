from decimal import Decimal
from functools import partial

import pytest
from strategy_callable.domain import Consignment, Money
from strategy_callable.rules import (
    RATE_RULES,
    TARIFF,
    PricingRule,
    Tariff,
    ZoneRate,
    flat_rate,
    per_kg,
)


def _quote_by_function_name(consignment: Consignment, name: str) -> tuple[str, Money]:
    """The brittle way to record a rule: introspect its name."""
    rule = RATE_RULES[name]
    return rule.__name__, rule(consignment)


def _make_loyalty_discount() -> PricingRule:
    """A closure that counts its own calls, so its answer depends on history."""
    calls = 0

    def rule(consignment: Consignment) -> Money:
        nonlocal calls
        calls += 1
        return Money(Decimal("25.00") - Decimal(calls), "EUR")

    return rule


def test_partials_and_rule_objects_have_no_name(consignment: Consignment) -> None:
    assert _quote_by_function_name(consignment, "flat")[0] == "flat_rate"
    assert flat_rate.__name__ == "flat_rate"
    for name in ("per-kg", "zone"):
        with pytest.raises(AttributeError, match="has no attribute '__name__'"):
            _quote_by_function_name(consignment, name)
    assert (lambda c: Money(Decimal(0), "EUR")).__name__ == "<lambda>"


def test_a_partial_has_no_value_equality() -> None:
    first = partial(per_kg, rate=Decimal("1.20"))
    second = partial(per_kg, rate=Decimal("1.20"))
    assert first != second
    assert first.func == second.func
    assert first.keywords == second.keywords


def test_a_rule_object_compares_and_hashes_by_value() -> None:
    other = ZoneRate(Tariff(frozendict({"EU": Decimal("0.50"), "ASIA": Decimal("1.50")})))
    rule = ZoneRate(TARIFF)
    assert rule == other
    assert hash(rule) == hash(other)
    assert repr(rule).startswith("ZoneRate(tariff=Tariff(")
    assert ZoneRate(Tariff(frozendict({"EU": Decimal("0.60")}))) != rule


def test_a_rule_with_hidden_state_is_not_reproducible(consignment: Consignment) -> None:
    rule = _make_loyalty_discount()
    first, second = rule(consignment), rule(consignment)
    assert first == Money(Decimal("24.00"), "EUR")
    assert second == Money(Decimal("23.00"), "EUR")
    assert first != second


def test_an_unbound_partial_fails_only_when_called(consignment: Consignment) -> None:
    # Assigned to the slot type first, as a registry entry is: mypy accepts the binding.
    unbound: PricingRule = partial(per_kg)
    with pytest.raises(TypeError, match="missing 1 required keyword-only argument: 'rate'"):
        unbound(consignment)
