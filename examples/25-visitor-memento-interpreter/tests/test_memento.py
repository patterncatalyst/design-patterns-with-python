import copy
from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest
from visitor_memento_interpreter.domain import AmendmentError, DocumentKind
from visitor_memento_interpreter.memento import Booking, rollback

type MementoForm = Callable[[Booking], AbstractContextManager[None]]


def _amend_badly(booking: Booking) -> None:
    """A batch that attaches a document, reweighs, then asks for a destination that is refused."""
    booking.attach(DocumentKind.DANGEROUS_GOODS_DECLARATION)
    booking.reweigh(Decimal(1200))
    booking.redirect("Hamburg")


def test_rollback_restores_the_request_after_a_failed_amendment(
    memento_form: MementoForm, booking: Booking
) -> None:
    with pytest.raises(AmendmentError), memento_form(booking):
        _amend_badly(booking)

    assert booking.request.kilograms == Decimal(100)
    assert booking.request.destination == "SGSIN"


def test_rollback_restores_the_attached_documents(booking: Booking) -> None:
    with pytest.raises(AmendmentError), rollback(booking):
        _amend_badly(booking)

    assert booking.documents == {DocumentKind.COMMERCIAL_INVOICE}


def test_a_shallow_memento_keeps_a_document_attached_after_rollback(
    shallow_memento: MementoForm, booking: Booking
) -> None:
    with pytest.raises(AmendmentError), shallow_memento(booking):
        _amend_badly(booking)

    assert booking.documents == {
        DocumentKind.COMMERCIAL_INVOICE,
        DocumentKind.DANGEROUS_GOODS_DECLARATION,
    }


def test_rollback_keeps_the_audit_trail(booking: Booking) -> None:
    with pytest.raises(AmendmentError), rollback(booking):
        _amend_badly(booking)

    assert booking.audit == [
        "attached dangerous goods declaration",
        "reweighed to 1200 kg",
        "refused redirect to 'Hamburg'",
        "rolled back",
    ]


def test_rollback_re_raises_the_amendment_error(booking: Booking) -> None:
    with pytest.raises(AmendmentError, match="not a UN/LOCODE"), rollback(booking):
        booking.redirect("Hamburg")


def test_a_block_that_succeeds_keeps_its_changes(booking: Booking) -> None:
    with rollback(booking):
        booking.attach(DocumentKind.DANGEROUS_GOODS_DECLARATION)
        booking.reweigh(Decimal(1200))
        booking.redirect("DEHAM")

    assert booking.request.kilograms == Decimal(1200)
    assert booking.request.destination == "DEHAM"
    assert DocumentKind.DANGEROUS_GOODS_DECLARATION in booking.documents
    assert "rolled back" not in booking.audit


def test_a_deepcopy_memento_erases_the_audit_trail_on_rollback(
    deep_memento: MementoForm, booking: Booking
) -> None:
    with pytest.raises(AmendmentError), deep_memento(booking):
        _amend_badly(booking)

    assert booking.audit == ["rolled back"]


def test_a_snapshot_shares_the_frozen_request_and_a_deepcopy_copies_it(booking: Booking) -> None:
    assert booking.snapshot().request is booking.request
    assert copy.deepcopy(booking).request is not booking.request
    assert copy.deepcopy(booking).request == booking.request


def test_a_snapshot_cannot_be_changed_at_run_time(booking: Booking) -> None:
    snapshot = booking.snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.request = booking.request  # type: ignore[misc]
