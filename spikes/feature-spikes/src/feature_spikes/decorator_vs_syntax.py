"""PDP-010: the GoF Decorator pattern and Python's ``@decorator`` syntax are independent.

GoF Decorator: objects that wrap objects, composed at runtime, same interface.
``@decorator`` syntax: sugar for ``fn = decorator(fn)``, applied once at definition time.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from decimal import Decimal
from functools import wraps
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Consignment:
    reference: str
    weight_kg: Decimal
    parcels: int = 1


# --- GoF Decorator: wrapper objects composed at runtime ---------------------------------------


class RateCalculator(Protocol):
    def quote(self, c: Consignment) -> Decimal: ...


@dataclass(frozen=True, slots=True)
class BaseRate:
    per_kg: Decimal

    def quote(self, c: Consignment) -> Decimal:
        return c.weight_kg * self.per_kg


@dataclass(frozen=True, slots=True)
class FuelSurcharge:
    inner: RateCalculator
    rate: Decimal

    def quote(self, c: Consignment) -> Decimal:
        return self.inner.quote(c) * (1 + self.rate)


@dataclass(frozen=True, slots=True)
class VolumeDiscount:
    inner: RateCalculator
    min_parcels: int
    rate: Decimal

    def quote(self, c: Consignment) -> Decimal:
        price = self.inner.quote(c)
        return price * (1 - self.rate) if c.parcels >= self.min_parcels else price


@dataclass(frozen=True, slots=True)
class Vat:
    inner: RateCalculator
    rate: Decimal

    def quote(self, c: Consignment) -> Decimal:
        return self.inner.quote(c) * (1 + self.rate)


# A config entry is a function that wraps a calculator: the stack is data, not source code.
type Layer = Callable[[RateCalculator], RateCalculator]


def compose(base: RateCalculator, layers: Sequence[Layer]) -> RateCalculator:
    """Wrap ``base`` with each layer in order: the last layer is the outermost."""
    calculator = base
    for layer in layers:
        calculator = layer(calculator)
    return calculator


# --- @decorator syntax: functions replaced at definition time ---------------------------------


class CarrierTimeout(Exception):  # noqa: N818 - domain name, not a generic error suffix
    """The carrier API did not answer."""


def retry[**P, R](
    *, attempts: int, on: tuple[type[BaseException], ...]
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Call the function up to ``attempts`` times while it raises one of ``on``."""

    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for _ in range(attempts - 1):
                try:
                    return fn(*args, **kwargs)
                except on:
                    continue
            return fn(*args, **kwargs)

        return wrapper

    return decorate


type AuditSink = Callable[[str, tuple[object, ...], dict[str, object]], None]


def audited[**P, R](sink: AuditSink) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Record every call (name, args, kwargs) to an injected sink."""

    def decorate(fn: Callable[P, R]) -> Callable[P, R]:
        @wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            sink(fn.__name__, args, kwargs)
            return fn(*args, **kwargs)

        return wrapper

    return decorate
