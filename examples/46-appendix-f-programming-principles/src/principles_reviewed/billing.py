"""A shipment, its invoice and its credits, and the reader that reports the amount due.

``remittance_line`` asks the shipment for ``amount_due``; it does not read the invoice itself.
"""

from dataclasses import dataclass
from functools import reduce

from principles_reviewed.domain import ConsignmentId, Money


@dataclass(frozen=True, slots=True)
class LineItem:
    description: str
    amount: Money


@dataclass(frozen=True, slots=True)
class Invoice:
    consignment_id: ConsignmentId
    lines: tuple[LineItem, ...]

    def __post_init__(self) -> None:
        if not self.lines:
            raise ValueError("an invoice needs at least one line")

    @property
    def total(self) -> Money:
        return reduce(Money.__add__, (line.amount for line in self.lines))


@dataclass(frozen=True, slots=True)
class Shipment:
    """A booked consignment's record: its invoice and the credits granted against it."""

    consignment_id: ConsignmentId
    invoice: Invoice
    credits: tuple[LineItem, ...] = ()

    def amount_due(self) -> Money:
        due = self.invoice.total
        for credit in self.credits:
            due = due - credit.amount
        return due


class SettlementError(ValueError):
    """A payment that is not the amount due."""


def settle(shipment: Shipment, payment: Money, /) -> Money:
    due = shipment.amount_due()
    if payment != due:
        raise SettlementError(f"{payment} does not settle {due}")
    return due


def remittance_line(shipment: Shipment, /) -> str:
    return f"{shipment.consignment_id} {shipment.amount_due()}"
