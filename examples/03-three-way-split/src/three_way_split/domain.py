"""Shipping value types shared by the witnesses."""

import math
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


@dataclass(frozen=True, slots=True)
class Weight:
    """A mass in kilograms: finite and strictly positive."""

    kilograms: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.kilograms) or self.kilograms <= 0:
            raise ValueError(f"weight must be finite and positive, got {self.kilograms!r}")


@dataclass(frozen=True, slots=True)
class Money:
    """An amount in one currency. Addition is defined only within a currency."""

    amount: Decimal
    currency: str

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """A shipment of a given weight bound for a destination in a pricing zone."""

    id: ConsignmentId
    weight: Weight
    zone: str
    destination: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Booked:
    consignment_id: ConsignmentId
    location: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Loaded:
    consignment_id: ConsignmentId
    location: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Departed:
    consignment_id: ConsignmentId
    location: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Cleared:
    consignment_id: ConsignmentId
    location: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Delivered:
    consignment_id: ConsignmentId
    location: str


type HandlingEvent = Booked | Loaded | Departed | Cleared | Delivered


@dataclass(frozen=True, slots=True)
class RateQuote:
    """The price quoted for one consignment."""

    consignment_id: ConsignmentId
    price: Money


@dataclass(frozen=True, slots=True)
class TrackingHistory:
    """The handling events of a consignment, read from a source on each iteration."""

    events: Iterable[HandlingEvent]

    def __iter__(self) -> Iterator[HandlingEvent]:
        return iter(self.events)


@dataclass(frozen=True, slots=True)
class CustomsDeclaration:
    """The result of the customs template: classification, duty and certificate."""

    consignment_id: ConsignmentId
    tariff_code: str
    duty: Money
    certificate: str


@dataclass(frozen=True, slots=True)
class CustomsHooks:
    """The steps that vary by destination; the order of the steps does not."""

    classify: Callable[[Consignment], str]
    assess_duty: Callable[[Consignment, str], Money]
    certify: Callable[[Consignment], str]


@dataclass(frozen=True, slots=True)
class Tariff:
    """The price per kilogram for each pricing zone."""

    per_kg_by_zone: Mapping[str, Money]

    def rate_for(self, zone: str) -> Money:
        return self.per_kg_by_zone[zone]
