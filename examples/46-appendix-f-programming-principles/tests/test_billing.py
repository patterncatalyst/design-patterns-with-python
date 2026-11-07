"""Money, invoices, amount due and settlement."""

import re
from decimal import Decimal

import pytest
from principles_reviewed.billing import Invoice, LineItem, SettlementError, Shipment, settle
from principles_reviewed.domain import ConsignmentId, Money

CN_1 = ConsignmentId("CN-1")


def test_an_invoice_totals_its_lines() -> None:
    invoice = Invoice(
        CN_1,
        (
            LineItem("freight", Money(Decimal("30.00"))),
            LineItem("duty", Money(Decimal("5.63"))),
        ),
    )
    assert invoice.total == Money(Decimal("35.63"))


def test_an_invoice_needs_a_line() -> None:
    with pytest.raises(ValueError, match=r"^an invoice needs at least one line$"):
        Invoice(CN_1, ())


def test_lines_in_two_currencies_have_no_total() -> None:
    invoice = Invoice(
        CN_1,
        (
            LineItem("freight", Money(Decimal("30.00"))),
            LineItem("duty", Money(Decimal("5.63"), "USD")),
        ),
    )
    with pytest.raises(ValueError, match=r"^cannot add USD to EUR$"):
        _ = invoice.total


def test_the_amount_due_subtracts_the_credits(credited: Shipment) -> None:
    assert credited.amount_due() == Money(Decimal("25.00"))


def test_a_credit_in_another_currency_is_refused(credited: Shipment) -> None:
    shipment = Shipment(
        credited.consignment_id,
        credited.invoice,
        (LineItem("damaged pallet", Money(Decimal("10.63"), "USD")),),
    )
    with pytest.raises(ValueError, match=r"^cannot subtract USD from EUR$"):
        shipment.amount_due()


def test_settle_accepts_the_amount_due(credited: Shipment) -> None:
    assert settle(credited, Money(Decimal("25.00"))) == Money(Decimal("25.00"))


@pytest.mark.parametrize("paid", ["24.99", "25.01"])
def test_settle_refuses_any_other_payment(credited: Shipment, paid: str) -> None:
    with pytest.raises(
        SettlementError, match=rf"^{re.escape(paid)} EUR does not settle 25\.00 EUR$"
    ):
        settle(credited, Money(Decimal(paid)))


def test_settle_refuses_the_right_amount_in_another_currency(credited: Shipment) -> None:
    with pytest.raises(SettlementError, match=r"^25\.00 USD does not settle 25\.00 EUR$"):
        settle(credited, Money(Decimal("25.00"), "USD"))
