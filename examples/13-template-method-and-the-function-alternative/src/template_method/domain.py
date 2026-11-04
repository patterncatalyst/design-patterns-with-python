"""Shipping values for the customs example: commodities, a consignment and a declaration."""

from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


class CustomsError(Exception):
    """A customs declaration could not be issued."""


@dataclass(frozen=True, slots=True)
class Money:
    """An amount and an ISO 4217 code. Only amounts in one currency add."""

    amount: Decimal
    currency: str

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise CustomsError(f"mixed currencies: {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)


@dataclass(frozen=True, slots=True)
class Commodity:
    """One kind of goods in a consignment, with its commercial value."""

    description: str
    value: Money


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """A shipment to a UN/LOCODE destination, carrying one or more commodities."""

    id: ConsignmentId
    destination: str
    commodities: tuple[Commodity, ...]


@dataclass(frozen=True, slots=True)
class DeclarationLine:
    """A commodity with the tariff code that classifies it."""

    description: str
    tariff_code: str
    value: Money


@dataclass(frozen=True, slots=True)
class CustomsDeclaration:
    """What is declared to a country: lines, their total value, the duty and the documents."""

    consignment_id: ConsignmentId
    country: str
    lines: tuple[DeclarationLine, ...]
    declared_value: Money
    duty: Money
    documents: tuple[str, ...]
