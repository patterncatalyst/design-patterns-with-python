from decimal import Decimal

import pytest
from command_undo.amendments import Redirect, Reweigh, SetInstructions
from command_undo.booking import Booking
from command_undo.domain import AmendmentError, BookingRequest, Weight


def kg(amount: int) -> Weight:
    return Weight(Decimal(amount))


def test_queued_amendments_apply_in_order(booking: Booking) -> None:
    booking.submit(Reweigh(kg(130)))
    booking.submit(Reweigh(kg(140)))
    booking.submit(Redirect("MYPKG"))
    booking.submit(SetInstructions(frozendict({"handling": "keep dry"})))
    assert booking.request.consignment.weight == kg(120)  # nothing runs until the batch does
    booking.apply_pending()
    assert booking.request.consignment.weight == kg(140)
    assert booking.request.consignment.destination == "MYPKG"
    assert booking.request.instructions == {"handling": "keep dry"}
    assert len(booking.pending) == 0
    booking.undo()
    booking.undo()
    assert booking.request.consignment.weight == kg(140)
    booking.undo()
    assert booking.request.consignment.weight == kg(130)
    booking.undo()
    assert booking.request.consignment.weight == kg(120)


def test_a_failing_batch_leaves_the_booking_unchanged(
    booking: Booking, booking_request: BookingRequest
) -> None:
    booking.amend(Reweigh(kg(125)))
    booking.undo()
    booking.submit(Reweigh(kg(130)))
    booking.submit(Redirect("nowhere"))
    request, undo_stack = booking.request, list(booking.undo_stack)
    redo_stack, pending = list(booking.redo_stack), list(booking.pending)
    with pytest.raises(AmendmentError, match="not a port code: 'nowhere'"):
        booking.apply_pending()
    assert booking.request == request == booking_request
    assert list(booking.undo_stack) == undo_stack
    assert list(booking.redo_stack) == redo_stack
    assert list(booking.pending) == pending == [Reweigh(kg(130)), Redirect("nowhere")]


def test_a_batch_clears_redo_and_records_one_inverse_per_amendment(booking: Booking) -> None:
    booking.amend(Reweigh(kg(125)))
    booking.undo()
    assert len(booking.redo_stack) == 1
    booking.submit(Reweigh(kg(130)))
    booking.submit(Redirect("MYPKG"))
    booking.apply_pending()
    assert len(booking.redo_stack) == 0
    assert list(booking.undo_stack) == [Reweigh(kg(120)), Redirect("SGSIN")]
