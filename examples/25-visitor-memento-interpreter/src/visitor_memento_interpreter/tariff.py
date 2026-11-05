"""A tariff as a tree of frozen nodes, with two readings: a price and a sentence."""

from dataclasses import dataclass
from decimal import Decimal
from typing import assert_never

from visitor_memento_interpreter.domain import Consignment, Money


@dataclass(frozen=True, slots=True)
class PerKg:
    rate: Money


@dataclass(frozen=True, slots=True)
class Flat:
    amount: Money


@dataclass(frozen=True, slots=True)
class Add:
    left: Expr
    right: Expr


@dataclass(frozen=True, slots=True)
class Max:
    left: Expr
    right: Expr


@dataclass(frozen=True, slots=True)
class OverWeight:
    """Use `then` above the limit and `otherwise` at or below it."""

    kilograms: Decimal
    then: Expr
    otherwise: Expr


type Expr = PerKg | Flat | Add | Max | OverWeight


def evaluate(expr: Expr, consignment: Consignment, /) -> Money:
    """Price a consignment under the rule."""
    match expr:
        case PerKg(rate):
            return rate.times(consignment.weight.kilograms)
        case Flat(amount):
            return amount
        case Add(left, right):
            return evaluate(left, consignment) + evaluate(right, consignment)
        case Max(left, right):
            return max(evaluate(left, consignment), evaluate(right, consignment))
        case OverWeight(kilograms, then, otherwise):
            chosen = then if consignment.weight.kilograms > kilograms else otherwise
            return evaluate(chosen, consignment)
        case _:
            assert_never(expr)


def explain(expr: Expr, /) -> str:
    """Write the rule back as a sentence."""
    match expr:
        case PerKg(rate):
            return f"{rate} per kg"
        case Flat(amount):
            return str(amount)
        case Add(left, right):
            return f"{explain(left)} + {explain(right)}"
        case Max(left, right):
            return f"the larger of {explain(left)} and {explain(right)}"
        case OverWeight(kilograms, then, otherwise):
            return f"over {kilograms} kg: {explain(then)}; otherwise {explain(otherwise)}"
        case _:
            assert_never(expr)


# Rates and fees are illustrative.
STANDARD_TARIFF: Expr = OverWeight(
    Decimal(1000),
    Add(PerKg(Money(Decimal("1.10"), "EUR")), Flat(Money(Decimal("25.00"), "EUR"))),
    Max(PerKg(Money(Decimal("1.20"), "EUR")), Flat(Money(Decimal("45.00"), "EUR"))),
)
