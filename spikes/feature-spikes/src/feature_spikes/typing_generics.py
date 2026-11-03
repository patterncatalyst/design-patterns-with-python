"""PDP-011: Protocol, callback Protocol, PEP 695 generics, ``override`` under mypy --strict."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol, override, runtime_checkable

from feature_spikes.decorator_vs_syntax import Consignment


@dataclass(frozen=True, slots=True)
class HazmatConsignment(Consignment):
    un_number: str = "UN1203"


class Quoter[T: Consignment](Protocol):
    """Prices consignments of one kind. Variance of ``T`` is inferred (PEP 695)."""

    def quote(self, c: T, /) -> Decimal: ...


class RateStrategy(Protocol):
    """Callback protocol: any callable with this signature, including plain functions."""

    def __call__(self, c: Consignment, /) -> Decimal: ...


@dataclass(frozen=True, slots=True)
class FlatQuoter:
    """Satisfies ``Quoter[Consignment]`` structurally: no base class."""

    price: Decimal

    def quote(self, c: Consignment, /) -> Decimal:
        return self.price


@dataclass(frozen=True, slots=True)
class HazmatQuoter(Quoter[HazmatConsignment]):
    """Explicit subclass of a Protocol: ``override`` is checked against the Protocol method."""

    premium: Decimal

    @override
    def quote(self, c: HazmatConsignment, /) -> Decimal:
        return self.premium if c.un_number else Decimal(0)


def cheapest[T](options: Iterable[T], key: Callable[[T], Decimal]) -> T:
    return min(options, key=key)


def price_with(strategy: RateStrategy, c: Consignment) -> Decimal:
    return strategy(c)


def price_all[T: Consignment](quoter: Quoter[T], consignments: Iterable[T]) -> list[Decimal]:
    return [quoter.quote(c) for c in consignments]


@runtime_checkable
class Describable(Protocol):
    def describe(self) -> str: ...
