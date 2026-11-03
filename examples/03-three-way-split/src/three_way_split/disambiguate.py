"""Names that mean two things.

The wrapper pattern and the @ syntax, Singleton, Proxy and interface.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property, wraps
from typing import Protocol, runtime_checkable

from three_way_split.dissolve import CarrierGateway, PricingRule
from three_way_split.domain import Consignment, ConsignmentId, HandlingEvent, Money, Weight

# Decorator the pattern: objects wrapping objects, composed at runtime.


@runtime_checkable
class RateCalculator(Protocol):
    def price(self, consignment: Consignment, /) -> Money: ...


@dataclass(frozen=True, slots=True)
class BaseRate:
    """The innermost calculator: applies a pricing rule."""

    rule: PricingRule

    def price(self, consignment: Consignment, /) -> Money:
        return self.rule(consignment)


@dataclass(frozen=True, slots=True)
class Surcharge:
    """Adds a fixed fee to whatever the wrapped calculator prices."""

    inner: RateCalculator
    fee: Money

    def price(self, consignment: Consignment, /) -> Money:
        return self.inner.price(consignment) + self.fee


def calculator_for(
    consignment: Consignment,
    base: RateCalculator,
    *,
    heavy_over: Weight,
    heavy_fee: Money,
) -> RateCalculator:
    """Choose the layers for this consignment while the program runs."""
    if consignment.weight.kilograms > heavy_over.kilograms:
        return Surcharge(base, heavy_fee)
    return base


# The @ syntax: a function rebound to a wrapper at definition time.


def audited[**P, R](sink: Callable[[str], None]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Report each call of the decorated function to ``sink``."""

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            sink(func.__name__)
            return func(*args, **kwargs)

        return wrapper

    return decorate


audit_trail: list[str] = []

_CARRIER_RATES = {"FASTLINE": Decimal("1.50"), "AIRCO": Decimal("3.00")}


@audited(audit_trail.append)
def quote_carrier(consignment: Consignment, carrier: str) -> Money:
    """Price a consignment at a carrier's per-kilogram rate."""
    amount = Decimal(str(consignment.weight.kilograms)) * _CARRIER_RATES[carrier]
    return Money(amount.quantize(Decimal("0.01")), "EUR")


# Singleton: a module is one instance. See tariff_table.py and loads.py.

# Lazy initialization: cached_property.


class LazyTrackingHistory:
    """Events fetched from a loader on first access and kept afterwards."""

    def __init__(self, loader: Callable[[], Iterable[HandlingEvent]]) -> None:
        self._loader = loader

    @cached_property
    def events(self) -> tuple[HandlingEvent, ...]:
        return tuple(self._loader())


# Proxy: forwards only the attributes it does not define.


class CarrierGatewayProxy:
    """Caches ``book`` per consignment and forwards every other attribute."""

    def __init__(self, inner: CarrierGateway) -> None:
        self._inner = inner
        self._booked: dict[ConsignmentId, str] = {}

    def book(self, consignment: Consignment, /) -> str:
        if consignment.id not in self._booked:
            self._booked[consignment.id] = self._inner.book(consignment)
        return self._booked[consignment.id]

    def __getattr__(self, name: str) -> object:
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._inner, name)
