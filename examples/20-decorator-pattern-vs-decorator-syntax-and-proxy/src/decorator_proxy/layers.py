"""The Decorator pattern: calculators that wrap calculators, stacked while the program runs."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Protocol

from decorator_proxy.domain import Consignment, Money, RatingError, Weight

_HUNDRED = Decimal(100)

# Illustrative figures.
HEAVY_OVER: Final = Weight(Decimal(500))
HEAVY_FEE: Final = Money(Decimal("15.00"), "EUR")
DANGEROUS_GOODS_FEE: Final = Money(Decimal("25.00"), "EUR")
# Tax percentages by the country prefix of a UN/LOCODE.
TAX_RATES: Final[Mapping[str, Decimal]] = frozendict({"NL": Decimal(21), "SG": Decimal(9)})


class RateCalculator(Protocol):
    def price(self, consignment: Consignment, /) -> Money: ...


@dataclass(frozen=True, slots=True)
class BaseRate:
    """The innermost calculator: a price per kilogram."""

    per_kg: Money

    def price(self, consignment: Consignment, /) -> Money:
        return self.per_kg.scaled(consignment.weight.kilograms)


@dataclass(frozen=True, slots=True)
class Discount:
    """Takes a percentage off whatever the wrapped calculator prices."""

    inner: RateCalculator
    percent: Decimal

    def price(self, consignment: Consignment, /) -> Money:
        return self.inner.price(consignment).scaled(1 - self.percent / _HUNDRED)


@dataclass(frozen=True, slots=True)
class Surcharge:
    """Adds a fixed fee to whatever the wrapped calculator prices."""

    inner: RateCalculator
    fee: Money

    def price(self, consignment: Consignment, /) -> Money:
        return self.inner.price(consignment) + self.fee


@dataclass(frozen=True, slots=True)
class Tax:
    """Adds a percentage on top of whatever the wrapped calculator prices."""

    inner: RateCalculator
    percent: Decimal

    def price(self, consignment: Consignment, /) -> Money:
        return self.inner.price(consignment).scaled(1 + self.percent / _HUNDRED)


type Layer = Callable[[RateCalculator], RateCalculator]


def discount(percent: Decimal) -> Layer:
    return lambda inner: Discount(inner, percent)


def surcharge(fee: Money) -> Layer:
    return lambda inner: Surcharge(inner, fee)


def tax(percent: Decimal) -> Layer:
    return lambda inner: Tax(inner, percent)


def compose(base: RateCalculator, layers: Sequence[Layer]) -> RateCalculator:
    """Wrap the base in each layer in turn, so the last layer is outermost."""
    calculator = base
    for layer in layers:
        calculator = layer(calculator)
    return calculator


def layers_for(consignment: Consignment) -> tuple[Layer, ...]:
    """Choose the layers for this consignment: surcharges first, destination tax last."""
    layers: list[Layer] = []
    if consignment.weight.kilograms > HEAVY_OVER.kilograms:
        layers.append(surcharge(HEAVY_FEE))
    if consignment.dangerous_goods:
        layers.append(surcharge(DANGEROUS_GOODS_FEE))
    country = consignment.destination[:2]
    try:
        layers.append(tax(TAX_RATES[country]))
    except KeyError:
        raise RatingError(f"no tax rate for country {country!r}") from None
    return tuple(layers)
