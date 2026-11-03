"""Patterns that Python's language features reduce to a few lines or nothing."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from decimal import Decimal
from functools import singledispatch
from itertools import batched
from typing import ClassVar, Protocol, runtime_checkable

from three_way_split.domain import (
    Booked,
    Cleared,
    Consignment,
    ConsignmentId,
    CustomsDeclaration,
    CustomsHooks,
    Delivered,
    Departed,
    HandlingEvent,
    Loaded,
    Money,
    RateQuote,
    TrackingHistory,
    Weight,
)

# Strategy: a callable.

type PricingRule = Callable[[Consignment], Money]

_CENT = Decimal("0.01")


def flat_rate(consignment: Consignment) -> Money:
    """A fixed price for any consignment."""
    return Money(Decimal("25.00"), "EUR")


def per_kg(consignment: Consignment, rate: Decimal = Decimal("1.20")) -> Money:
    """A price proportional to weight."""
    amount = (Decimal(str(consignment.weight.kilograms)) * rate).quantize(_CENT)
    return Money(amount, "EUR")


def quote(consignment: Consignment, rule: PricingRule) -> RateQuote:
    """Price a consignment with whichever rule the caller passes."""
    return RateQuote(consignment.id, rule(consignment))


# Factory Method: a class is already a factory.


@runtime_checkable
class CarrierGateway(Protocol):
    """What the booking code needs from a carrier."""

    def book(self, consignment: Consignment, /) -> str: ...


class FastlineGateway:
    code: ClassVar[str] = "FASTLINE"

    def book(self, consignment: Consignment, /) -> str:
        return f"FASTLINE:{consignment.id}"


class AircoGateway:
    code: ClassVar[str] = "AIRCO"

    def book(self, consignment: Consignment, /) -> str:
        return f"AIRCO:{consignment.id}"


GATEWAYS: dict[str, Callable[[], CarrierGateway]] = {
    "FASTLINE": FastlineGateway,
    "AIRCO": AircoGateway,
}


# Null Object: an optional the type checker enforces.


def find_gateway(code: str) -> CarrierGateway | None:
    """Return a gateway for a carrier code, or None when the code is unknown."""
    factory = GATEWAYS.get(code)
    if factory is None:
        return None
    return factory()


# Iterator: a generator.


def pages(history: TrackingHistory, size: int) -> Iterator[tuple[HandlingEvent, ...]]:
    """Yield the history in pages of at most ``size`` events, reading lazily."""
    yield from batched(history, size, strict=False)


# Template Method: a function that takes hooks.


def declare_customs(consignment: Consignment, *, hooks: CustomsHooks) -> CustomsDeclaration:
    """Run the fixed customs steps in order, using the hooks for the varying parts."""
    tariff_code = hooks.classify(consignment)
    duty = hooks.assess_duty(consignment, tariff_code)
    certificate = hooks.certify(consignment)
    return CustomsDeclaration(consignment.id, tariff_code, duty, certificate)


# Builder: a keyword-only dataclass.


@dataclass(frozen=True, slots=True, kw_only=True)
class BookingRequest:
    consignment_id: ConsignmentId
    origin: str
    destination: str
    weight: Weight
    carrier: str = "FASTLINE"
    service: str = "standard"
    insured: bool = False
    reference: str | None = None


# Visitor: singledispatch over the event classes, with no accept method.


@singledispatch
def describe(event: object) -> str:
    """Describe a handling event; unregistered types fall back to this."""
    return "unrecognised event"


@describe.register
def _(event: Booked) -> str:
    return f"{event.consignment_id} booked at {event.location}"


@describe.register
def _(event: Loaded) -> str:
    return f"{event.consignment_id} loaded at {event.location}"


@describe.register
def _(event: Departed) -> str:
    return f"{event.consignment_id} departed {event.location}"


@describe.register
def _(event: Cleared) -> str:
    return f"{event.consignment_id} cleared customs at {event.location}"


@describe.register
def _(event: Delivered) -> str:
    return f"{event.consignment_id} delivered at {event.location}"


# Registry: __init_subclass__.


class DuplicateCarrierError(Exception):
    """Two carrier classes claimed the same code."""


CARRIERS: dict[str, type[CarrierBase]] = {}


class CarrierBase(ABC):
    """A nominal base class whose subclasses register themselves by carrier code."""

    def __init_subclass__(cls, *, code: str, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if code in CARRIERS:
            raise DuplicateCarrierError(f"carrier code {code!r} is already registered")
        CARRIERS[code] = cls

    @abstractmethod
    def book(self, consignment: Consignment, /) -> str: ...
