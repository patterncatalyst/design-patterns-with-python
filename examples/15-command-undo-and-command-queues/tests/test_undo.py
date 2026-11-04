from dataclasses import dataclass, replace
from decimal import Decimal

import pytest
from command_undo.amendments import Redirect, Reweigh
from command_undo.booking import Booking
from command_undo.domain import AmendmentError, BookingRequest, Weight


def kg(amount: int) -> Weight:
    return Weight(Decimal(amount))


@dataclass(frozen=True, slots=True)
class _PrecomputedReweigh:
    """The shape that records the old value when the command is built."""

    before: Weight
    after: Weight

    def do(self, request: BookingRequest) -> BookingRequest:
        return replace(request, consignment=replace(request.consignment, weight=self.after))

    def undo(self, request: BookingRequest) -> BookingRequest:
        return replace(request, consignment=replace(request.consignment, weight=self.before))


def test_undo_and_redo_walk_the_history(booking: Booking) -> None:
    booking.amend(Reweigh(kg(130)))
    booking.amend(Redirect("MYPKG"))
    assert booking.request.consignment.destination == "MYPKG"
    booking.undo()
    assert booking.request.consignment.destination == "SGSIN"
    assert booking.request.consignment.weight == kg(130)
    booking.undo()
    assert booking.request.consignment.weight == kg(120)
    assert (len(booking.undo_stack), len(booking.redo_stack)) == (0, 2)
    booking.redo()
    assert booking.request.consignment.weight == kg(130)
    booking.redo()
    assert booking.request.consignment.destination == "MYPKG"
    assert (len(booking.undo_stack), len(booking.redo_stack)) == (2, 0)


def test_a_new_amendment_clears_redo(booking: Booking) -> None:
    booking.amend(Reweigh(kg(130)))
    booking.undo()
    assert len(booking.redo_stack) == 1
    booking.amend(Redirect("MYPKG"))
    assert len(booking.redo_stack) == 0
    with pytest.raises(AmendmentError, match="nothing to redo"):
        booking.redo()
    assert booking.request.consignment.weight == kg(120)
    assert booking.request.consignment.destination == "MYPKG"


@pytest.mark.parametrize("operation", ["undo", "redo"])
def test_undo_or_redo_with_nothing_recorded_is_an_amendment_error(
    booking: Booking, operation: str
) -> None:
    before = booking.request
    with pytest.raises(AmendmentError, match=f"nothing to {operation}"):
        getattr(booking, operation)()
    assert booking.request == before


def test_two_amendments_undone_restore_the_original_request(
    booking: Booking, booking_request: BookingRequest
) -> None:
    booking.amend(Reweigh(kg(130)))
    booking.amend(Redirect("MYPKG"))
    booking.undo()
    booking.undo()
    assert booking.request == booking_request


def test_an_inverse_captured_when_queued_restores_a_stale_weight(
    booking: Booking, booking_request: BookingRequest
) -> None:
    # Both commands are built while the weight is 120, so both record 120 as "before".
    queued = [
        _PrecomputedReweigh(before=kg(120), after=kg(130)),
        _PrecomputedReweigh(before=kg(120), after=kg(140)),
    ]
    request = booking_request
    for command in queued:
        request = command.do(request)
    assert request.consignment.weight == kg(140)
    assert queued[-1].undo(request).consignment.weight == kg(120)  # 130 expected
    # The inverse computed when the command runs gives the weight the request actually had.
    booking.amend(Reweigh(kg(130)))
    booking.amend(Reweigh(kg(140)))
    booking.undo()
    assert booking.request.consignment.weight == kg(130)


def test_a_bounded_history_forgets_the_oldest_amendment(booking_request: BookingRequest) -> None:
    booking = Booking(booking_request, history_limit=2)
    booking.amend(Reweigh(kg(130)))
    booking.amend(Reweigh(kg(140)))
    booking.amend(Reweigh(kg(150)))
    booking.undo()
    booking.undo()
    with pytest.raises(AmendmentError, match="nothing to undo"):
        booking.undo()
    assert booking.request.consignment.weight == kg(130)


def test_a_frozen_request_is_a_safe_snapshot(
    booking: Booking, booking_request: BookingRequest
) -> None:
    snapshot = booking.request
    booking.amend(Reweigh(kg(130)))
    booking.amend(Redirect("MYPKG"))
    assert booking.request != snapshot
    assert snapshot == booking_request
    assert snapshot.consignment.weight == kg(120)
