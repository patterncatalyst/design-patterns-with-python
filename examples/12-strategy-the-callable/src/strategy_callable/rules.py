"""Pricing rules as callables, a read-only registry to choose one by name, and quote."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from functools import partial

from strategy_callable.domain import Consignment, Money, RateQuote, RatingError

_CENT = Decimal("0.01")

type PricingRule = Callable[[Consignment], Money]


def flat_rate(consignment: Consignment) -> Money:
    return Money(Decimal("25.00"), "EUR")


def per_kg(consignment: Consignment, *, rate: Decimal) -> Money:
    """Price by weight at a rate that the caller binds, for example with partial."""
    amount = (consignment.weight.kilograms * rate).quantize(_CENT, rounding=ROUND_HALF_UP)
    return Money(amount, "EUR")


@dataclass(frozen=True, slots=True)
class Tariff:
    """Rate per kilogram by zone."""

    per_kg_by_zone: frozendict[str, Decimal]
    currency: str = "EUR"


@dataclass(frozen=True, slots=True)
class ZoneRate:
    """A rule object: configured by a tariff, equal and hashable by value."""

    tariff: Tariff

    def __call__(self, consignment: Consignment, /) -> Money:
        try:
            rate = self.tariff.per_kg_by_zone[consignment.zone]
        except KeyError:
            raise RatingError(f"no tariff for zone {consignment.zone!r}") from None
        amount = (consignment.weight.kilograms * rate).quantize(_CENT, rounding=ROUND_HALF_UP)
        return Money(amount, self.tariff.currency)


TARIFF = Tariff(frozendict({"EU": Decimal("0.50"), "ASIA": Decimal("1.50")}))

RATE_RULES: Mapping[str, PricingRule] = frozendict(
    {
        "flat": flat_rate,
        "per-kg": partial(per_kg, rate=Decimal("1.20")),
        "zone": ZoneRate(TARIFF),
    }
)


def quote(
    consignment: Consignment, rule_name: str, *, rules: Mapping[str, PricingRule] = RATE_RULES
) -> RateQuote:
    """Price a consignment with the rule registered under rule_name and record the name."""
    try:
        rule = rules[rule_name]
    except KeyError:
        raise RatingError(f"no pricing rule named {rule_name!r}") from None
    return RateQuote(consignment.id, rule_name, rule(consignment))
