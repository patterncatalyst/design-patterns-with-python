from collections.abc import Callable
from typing import Protocol

import pytest
from observer.domain import HandlingEvent, HandlingKind
from observer.signal import Signal, Subscriber, Unsubscribe
from observer.tracking import TrackingHistory

Log = list[tuple[str, HandlingKind]]
Labelled = Callable[[str], Subscriber[HandlingEvent]]
MakeEvent = Callable[[HandlingKind], HandlingEvent]


class _Form(Protocol):
    def subscribe(self, subscriber: Subscriber[HandlingEvent], /) -> Unsubscribe: ...

    def publish(self, event: HandlingEvent, /) -> None: ...


def test_subscribers_are_called_in_subscription_order(
    signal_form: _Form, labelled: Labelled, event: MakeEvent, log: Log
) -> None:
    signal_form.subscribe(labelled("first"))
    signal_form.subscribe(labelled("second"))
    signal_form.subscribe(labelled("third"))

    signal_form.publish(event(HandlingKind.LOADED))

    assert log == [
        ("first", HandlingKind.LOADED),
        ("second", HandlingKind.LOADED),
        ("third", HandlingKind.LOADED),
    ]


def test_an_unsubscribed_subscriber_gets_no_more_events(
    signal_form: _Form, labelled: Labelled, event: MakeEvent, log: Log
) -> None:
    signal_form.subscribe(labelled("kept"))
    unsubscribe = signal_form.subscribe(labelled("removed"))
    signal_form.publish(event(HandlingKind.LOADED))

    unsubscribe()
    signal_form.publish(event(HandlingKind.DEPARTED))

    assert log == [
        ("kept", HandlingKind.LOADED),
        ("removed", HandlingKind.LOADED),
        ("kept", HandlingKind.DEPARTED),
    ]


def test_subscribing_twice_delivers_once(
    signal: Signal[HandlingEvent], labelled: Labelled, event: MakeEvent, log: Log
) -> None:
    function = labelled("function")
    history = TrackingHistory()
    signal.subscribe(function)
    signal.subscribe(function)
    signal.subscribe(history.record)
    signal.subscribe(history.record)

    signal.publish(event(HandlingKind.LOADED))

    assert log == [("function", HandlingKind.LOADED)]
    assert history.events == (event(HandlingKind.LOADED),)
    assert len(signal) == 2


def test_one_failing_subscriber_does_not_stop_the_rest(
    signal: Signal[HandlingEvent], labelled: Labelled, event: MakeEvent, log: Log
) -> None:
    def store_down(_event: HandlingEvent, /) -> None:
        raise RuntimeError("history store down")

    signal.subscribe(labelled("before"))
    signal.subscribe(store_down)
    signal.subscribe(labelled("after"))

    with pytest.raises(ExceptionGroup) as raised:
        signal.publish(event(HandlingKind.DEPARTED))

    assert log == [("before", HandlingKind.DEPARTED), ("after", HandlingKind.DEPARTED)]
    assert len(raised.value.exceptions) == 1
    assert isinstance(raised.value.exceptions[0], RuntimeError)
    assert str(raised.value.exceptions[0]) == "history store down"


def test_a_plain_list_stops_at_the_first_failing_subscriber(
    list_signal: _Form, labelled: Labelled, event: MakeEvent, log: Log
) -> None:
    def store_down(_event: HandlingEvent, /) -> None:
        raise RuntimeError("history store down")

    list_signal.subscribe(labelled("before"))
    list_signal.subscribe(store_down)
    list_signal.subscribe(labelled("after"))

    with pytest.raises(RuntimeError, match="history store down"):
        list_signal.publish(event(HandlingKind.DEPARTED))

    assert log == [("before", HandlingKind.DEPARTED)]


@pytest.mark.parametrize("count", [1, 2], ids=["one", "two"])
def test_every_failure_is_reported_after_delivery(
    signal: Signal[HandlingEvent],
    labelled: Labelled,
    event: MakeEvent,
    log: Log,
    count: int,
) -> None:
    errors = [RuntimeError(f"failure {number}") for number in range(count)]

    def failing(error: RuntimeError) -> Subscriber[HandlingEvent]:
        def raise_it(_event: HandlingEvent, /) -> None:
            raise error

        return raise_it

    for error in errors:
        signal.subscribe(failing(error))
    signal.subscribe(labelled("last"))

    with pytest.raises(ExceptionGroup, match="subscribers failed") as raised:
        signal.publish(event(HandlingKind.CLEARED))

    assert raised.value.exceptions == tuple(errors)
    assert log == [("last", HandlingKind.CLEARED)]


def test_tracking_history_records_events_in_order(
    signal: Signal[HandlingEvent], event: MakeEvent
) -> None:
    history = TrackingHistory()
    signal.subscribe(history.record)

    for kind in (HandlingKind.BOOKED, HandlingKind.LOADED, HandlingKind.DEPARTED):
        signal.publish(event(kind))

    assert [e.kind for e in history.events] == [
        HandlingKind.BOOKED,
        HandlingKind.LOADED,
        HandlingKind.DEPARTED,
    ]


def test_the_signal_accepts_new_events_after_a_failed_delivery(
    signal: Signal[HandlingEvent], event: MakeEvent
) -> None:
    history = TrackingHistory()
    failing = [True]

    def flaky(_event: HandlingEvent, /) -> None:
        if failing:
            failing.clear()
            raise RuntimeError("history store down")

    signal.subscribe(flaky)
    signal.subscribe(history.record)
    with pytest.raises(ExceptionGroup):
        signal.publish(event(HandlingKind.LOADED))

    signal.publish(event(HandlingKind.DEPARTED))

    assert [e.kind for e in history.events] == [HandlingKind.LOADED, HandlingKind.DEPARTED]


class _Abort(BaseException):
    """Not an `Exception`, so delivery does not collect it."""


def test_the_signal_accepts_new_events_after_an_interrupted_delivery(
    signal: Signal[HandlingEvent], event: MakeEvent
) -> None:
    history = TrackingHistory()
    interrupt = [True]

    def interrupting(_event: HandlingEvent, /) -> None:
        if interrupt:
            interrupt.clear()
            raise _Abort

    signal.subscribe(interrupting)
    signal.subscribe(history.record)
    with pytest.raises(_Abort):
        signal.publish(event(HandlingKind.LOADED))

    signal.publish(event(HandlingKind.DEPARTED))

    assert [e.kind for e in history.events] == [HandlingKind.DEPARTED]
