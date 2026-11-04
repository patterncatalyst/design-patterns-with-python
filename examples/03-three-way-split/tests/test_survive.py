from collections import deque
from collections.abc import Callable
from functools import partial

from three_way_split.domain import Consignment, Weight
from three_way_split.survive import Amendment, Booking


def test_deferred_command_is_a_partial_in_a_deque(consignment: Consignment) -> None:
    booking = Booking(consignment)
    queue: deque[Callable[[], None]] = deque()
    queue.append(partial(booking.reweigh, Weight(130.0)))
    queue.append(partial(booking.reweigh, Weight(140.0)))

    assert booking.consignment.weight == Weight(120.0)

    queue.popleft()()
    assert booking.consignment.weight == Weight(130.0)
    queue.popleft()()
    assert booking.consignment.weight == Weight(140.0)
    assert not queue


def test_undo_needs_a_command_object(consignment: Consignment) -> None:
    booking = Booking(consignment)
    deferred = partial(booking.reweigh, Weight(130.0))
    assert not hasattr(deferred, "undo")

    first = Amendment(before=booking.consignment.weight, after=Weight(130.0))
    booking.amend(first)
    second = Amendment(before=booking.consignment.weight, after=Weight(140.0))
    booking.amend(second)
    assert booking.consignment.weight == Weight(140.0)

    booking.undo_last()
    assert booking.consignment.weight == Weight(130.0)
    booking.undo_last()
    assert booking.consignment.weight == Weight(120.0)
    assert booking.applied == []
