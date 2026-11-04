"""One behaviour table, run against the registry of callables and against a class per strategy."""

import ast
import inspect
from abc import ABC, abstractmethod
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest
from strategy_callable import rules
from strategy_callable.domain import Consignment, ConsignmentId, Money, Weight
from strategy_callable.rules import RATE_RULES

_CENT = Decimal("0.01")


class _PricingStrategy(ABC):
    @abstractmethod
    def price(self, consignment: Consignment) -> Money: ...


class _FlatRateStrategy(_PricingStrategy):
    def price(self, consignment: Consignment) -> Money:
        return Money(Decimal("25.00"), "EUR")


class _PerKgStrategy(_PricingStrategy):
    def price(self, consignment: Consignment) -> Money:
        amount = consignment.weight.kilograms * Decimal("1.20")
        return Money(amount.quantize(_CENT, rounding=ROUND_HALF_UP), "EUR")


class _ZoneRateStrategy(_PricingStrategy):
    def price(self, consignment: Consignment) -> Money:
        amount = consignment.weight.kilograms * {"EU": Decimal("0.50")}[consignment.zone]
        return Money(amount.quantize(_CENT, rounding=ROUND_HALF_UP), "EUR")


_STRATEGIES: frozendict[str, _PricingStrategy] = frozendict(
    {"flat": _FlatRateStrategy(), "per-kg": _PerKgStrategy(), "zone": _ZoneRateStrategy()}
)

_BEHAVIOUR_TABLE = [
    pytest.param("flat", "10", "EU", "25.00", id="flat"),
    pytest.param("per-kg", "0.1875", "EU", "0.23", id="per-kg"),
    pytest.param("zone", "28.85", "EU", "14.43", id="zone"),
]


def _consignment(kilograms: str, zone: str) -> Consignment:
    return Consignment(
        id=ConsignmentId("CN-00000003"),
        weight=Weight(Decimal(kilograms)),
        zone=zone,
        destination="NLRTM",
    )


@pytest.mark.parametrize(("key", "kilograms", "zone", "expected"), _BEHAVIOUR_TABLE)
def test_each_registered_rule_prices_the_behaviour_table(
    key: str, kilograms: str, zone: str, expected: str
) -> None:
    assert RATE_RULES[key](_consignment(kilograms, zone)) == Money(Decimal(expected), "EUR")


@pytest.mark.parametrize(("key", "kilograms", "zone", "expected"), _BEHAVIOUR_TABLE)
def test_a_class_per_strategy_passes_the_same_table(
    key: str, kilograms: str, zone: str, expected: str
) -> None:
    assert _STRATEGIES[key].price(_consignment(kilograms, zone)) == Money(Decimal(expected), "EUR")


def _strategy_classes(source: str) -> list[str]:
    """Names of the classes that define __call__ or price, the one method a strategy exposes."""
    return [
        node.name
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ClassDef)
        and any(
            isinstance(item, ast.FunctionDef) and item.name in {"__call__", "price"}
            for item in node.body
        )
    ]


def test_the_class_design_declares_four_strategy_classes_where_the_rules_declare_one() -> None:
    assert _strategy_classes(inspect.getsource(rules)) == ["ZoneRate"]
    assert sorted(_strategy_classes(Path(__file__).read_text())) == [
        "_FlatRateStrategy",
        "_PerKgStrategy",
        "_PricingStrategy",
        "_ZoneRateStrategy",
    ]
