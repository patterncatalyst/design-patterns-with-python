"""Billing: an invoice of line items, and a settlement that must match its total."""

from dataclasses import dataclass

from final_project.domain import ConsignmentId, Money


@dataclass(frozen=True, slots=True)
class LineItem:
    description: str
    amount: Money


@dataclass(frozen=True, slots=True)
class Invoice:
    """At least one line; every line in one currency."""

    consignment_id: ConsignmentId
    lines: tuple[LineItem, ...]

    @property
    def total(self) -> Money:
        first, *rest = (line.amount for line in self.lines)
        return sum(rest, first)


@dataclass(frozen=True, slots=True)
class Settlement:
    invoice: Invoice
    paid: Money


class SettlementError(ValueError):
    """The payment is not the invoice total."""


def settle(invoice: Invoice, payment: Money, /) -> Settlement:
    if payment != invoice.total:
        raise SettlementError(f"{payment.amount} does not settle {invoice.total.amount}")
    return Settlement(invoice, payment)
