"""Shipping value types for the rate quote."""

import math
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class RatingError(Exception):
    """A consignment cannot be rated: unknown zone or no tax rule for the destination."""


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
    """A shipment of a given weight bound for a UN/LOCODE destination in a pricing zone."""

    id: ConsignmentId
    weight: Weight
    zone: str
    destination: str


@dataclass(frozen=True, slots=True)
class RateQuote:
    """The net price and the tax on it for one consignment."""

    consignment_id: ConsignmentId
    net: Money
    tax: Money

    @property
    def total(self) -> Money:
        return self.net + self.tax


@dataclass(frozen=True, slots=True)
class Tariff:
    """The price per kilogram for each pricing zone."""

    per_kg_by_zone: Mapping[str, Money]

    def rate_for(self, zone: str) -> Money:
        try:
            return self.per_kg_by_zone[zone]
        except KeyError:
            raise RatingError(f"no tariff for zone {zone!r}") from None
