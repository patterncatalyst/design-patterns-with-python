"""Every test that asserts a subscriber was dropped or kept alive builds it in a helper or deletes
every name that refers to it, then calls ``gc.collect()`` before asserting. CPython usually frees
an object at its last reference, but the language promises no immediate finalisation, and a
reference cycle waits for the collector."""

import gc
import weakref
from collections.abc import Callable
from typing import Protocol, override

import pytest
from observer.domain import HandlingEvent, HandlingKind
from observer.signal import Signal, Subscriber, Unsubscribe
from observer.tracking import TrackingHistory

MakeEvent = Callable[[HandlingKind], HandlingEvent]


class _Form(Protocol):
    def subscribe(self, subscriber: Subscriber[HandlingEvent], /) -> Unsubscribe: ...

    def publish(self, event: HandlingEvent, /) -> None: ...


def _abandon_history(signal: Signal[HandlingEvent]) -> weakref.ref[TrackingHistory]:
    """Subscribe a history's bound method and return only a weak reference to the history."""
    history = TrackingHistory()
    signal.subscribe(history.record)
    return weakref.ref(history)


def test_a_plain_list_keeps_an_abandoned_subscriber_alive(
    list_signal: _Form, event: MakeEvent
) -> None:
    history = TrackingHistory()
    list_signal.subscribe(history.record)
    history_ref = weakref.ref(history)
    del history

    gc.collect()

    survivor = history_ref()
    assert survivor is not None
    list_signal.publish(event(HandlingKind.LOADED))
    assert survivor.events == (event(HandlingKind.LOADED),)


def test_a_bound_method_subscriber_is_dropped_when_its_owner_goes(
    signal: Signal[HandlingEvent], event: MakeEvent
) -> None:
    history = TrackingHistory()
    signal.subscribe(history.record)
    history_ref = weakref.ref(history)
    assert len(signal) == 1
    del history

    gc.collect()

    assert history_ref() is None
    assert len(signal) == 0
    signal.publish(event(HandlingKind.LOADED))  # reaches no one, and raises nothing


def test_a_subscriber_nobody_else_holds_is_dropped(
    signal: Signal[HandlingEvent], event: MakeEvent
) -> None:
    signal.subscribe(TrackingHistory().record)

    gc.collect()

    assert len(signal) == 0
    signal.publish(event(HandlingKind.LOADED))


def test_a_lambda_subscriber_is_held_strongly(
    signal: Signal[HandlingEvent], event: MakeEvent
) -> None:
    seen: list[HandlingKind] = []
    signal.subscribe(lambda e: seen.append(e.kind))

    gc.collect()  # a weak reference to this lambda would be dead by now

    assert len(signal) == 1
    signal.publish(event(HandlingKind.LOADED))
    assert seen == [HandlingKind.LOADED]


def _subscribe_a_lambda_over_a_history(
    signal: Signal[HandlingEvent],
) -> weakref.ref[TrackingHistory]:
    history = TrackingHistory()
    signal.subscribe(lambda e: history.record(e))
    return weakref.ref(history)


def test_a_lambda_that_closes_over_its_owner_keeps_it_alive(
    signal: Signal[HandlingEvent], event: MakeEvent
) -> None:
    history_ref = _subscribe_a_lambda_over_a_history(signal)

    gc.collect()

    history = history_ref()
    assert history is not None
    signal.publish(event(HandlingKind.LOADED))
    assert history.events == (event(HandlingKind.LOADED),)


class _Slotted:
    """A subscriber owner with slots and no weak-reference slot."""

    __slots__ = ("seen",)

    def __init__(self) -> None:
        self.seen: list[HandlingKind] = []

    def record(self, event: HandlingEvent, /) -> None:
        self.seen.append(event.kind)


def test_a_slotted_subscriber_without_a_weakref_slot_is_refused(
    signal: Signal[HandlingEvent],
) -> None:
    with pytest.raises(TypeError, match="cannot create weak reference"):
        signal.subscribe(_Slotted().record)

    assert len(signal) == 0


class _Cyclic(TrackingHistory):
    """A history that refers to itself, so only the collector can free it."""

    def __init__(self) -> None:
        super().__init__()
        self.itself = self


def _subscribe_a_cyclic_history(
    signal: Signal[HandlingEvent],
) -> weakref.ref[_Cyclic]:
    history = _Cyclic()
    signal.subscribe(history.record)
    return weakref.ref(history)


@pytest.mark.usefixtures("collector_paused")
def test_a_subscriber_in_a_reference_cycle_stays_until_the_collector_runs(
    signal: Signal[HandlingEvent],
) -> None:
    history_ref = _subscribe_a_cyclic_history(signal)

    assert history_ref() is not None  # automatic collection is paused: only a cycle holds it
    assert len(signal) == 1

    gc.collect()

    assert history_ref() is None
    assert len(signal) == 0


def _subscribe_and_abandon(
    signal: Signal[HandlingEvent],
) -> tuple[weakref.ref[TrackingHistory], Unsubscribe]:
    history = TrackingHistory()
    unsubscribe = signal.subscribe(history.record)
    return weakref.ref(history), unsubscribe


def test_a_subscriber_that_dies_during_delivery_is_skipped(
    signal: Signal[HandlingEvent], event: MakeEvent
) -> None:
    told: list[HandlingKind] = []

    class _Told(TrackingHistory):
        @override
        def record(self, received: HandlingEvent, /) -> None:
            told.append(received.kind)

    holders = [_Told()]
    history_ref = weakref.ref(holders[0])

    def drop_the_history(_event: HandlingEvent, /) -> None:
        holders.clear()
        gc.collect()  # the delivery snapshot holds only weak references to bound methods

    signal.subscribe(drop_the_history)
    signal.subscribe(holders[0].record)

    signal.publish(event(HandlingKind.LOADED))  # raises nothing: the dead entry is skipped

    assert history_ref() is None
    assert told == []


def test_unsubscribe_is_safe_after_the_owner_has_gone(signal: Signal[HandlingEvent]) -> None:
    history_ref, unsubscribe = _subscribe_and_abandon(signal)
    gc.collect()
    assert history_ref() is None

    unsubscribe()
    unsubscribe()

    assert len(signal) == 0
