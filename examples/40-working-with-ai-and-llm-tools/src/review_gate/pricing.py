"""The idiomatic pricing module: rules are callables in a read-only table, chosen by name."""

from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal
from functools import partial

from review_gate.domain import Consignment, Money, RatingError

type PricingRule = Callable[[Consignment], Money]

CENT = Decimal("0.01")


def flat(consignment: Consignment, /) -> Money:
    """Ten euros whatever the weight."""
    return Money(Decimal("10.00"))


def per_kg(consignment: Consignment, /, *, rate: Decimal) -> Money:
    """Weight times a rate per kilogram, rounded half up to the cent."""
    return Money((consignment.weight.kilograms * rate).quantize(CENT, rounding=ROUND_HALF_UP))


RULES: frozendict[str, PricingRule] = frozendict(
    {"flat": flat, "per_kg": partial(per_kg, rate=Decimal("0.45"))}
)


def price(rule: str, consignment: Consignment, /) -> Money:
    """Price a consignment by the named rule; an unknown name is a ``RatingError``."""
    try:
        chosen = RULES[rule]
    except KeyError:
        raise RatingError(f"unknown rule {rule}") from None
    return chosen(consignment)
