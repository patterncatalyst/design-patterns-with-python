from collections.abc import Callable
from typing import Protocol

from observer.domain import HandlingEvent, HandlingKind
from observer.signal import Signal, Subscriber, Unsubscribe
from observer.tracking import TrackingHistory

Log = list[tuple[str, HandlingKind]]
Labelled = Callable[[str], Subscriber[HandlingEvent]]
MakeEvent = Callable[[HandlingKind], HandlingEvent]


class _Form(Protocol):
    def subscribe(self, subscriber: Subscriber[HandlingEvent], /) -> Unsubscribe: ...

    def publish(self, event: HandlingEvent, /) -> None: ...


def test_a_subscriber_added_during_delivery_gets_the_next_event(
    signal: Signal[HandlingEvent], labelled: Labelled, event: MakeEvent, log: Log
) -> None:
    late = labelled("late")
    added = [False]

    def adder(_event: HandlingEvent, /) -> None:
        log.append(("adder", _event.kind))
        if not added[0]:
            added[0] = True
            signal.subscribe(late)

    signal.subscribe(labelled("first"))
    signal.subscribe(adder)

    signal.publish(event(HandlingKind.LOADED))
    signal.publish(event(HandlingKind.DEPARTED))

    assert log == [
        ("first", HandlingKind.LOADED),
        ("adder", HandlingKind.LOADED),
        ("first", HandlingKind.DEPARTED),
        ("adder", HandlingKind.DEPARTED),
        ("late", HandlingKind.DEPARTED),
    ]


def _remover_first(form: _Form, labelled: Labelled, log: Log) -> None:
    """Subscribe a subscriber that removes itself, then two more, in that order."""
    holder: list[Unsubscribe] = []

    def remover(event: HandlingEvent, /) -> None:
        log.append(("remover", event.kind))
        holder[0]()

    holder.append(form.subscribe(remover))
    form.subscribe(labelled("a"))
    form.subscribe(labelled("b"))


def test_unsubscribing_during_delivery_does_not_skip_another_subscriber(
    signal: Signal[HandlingEvent], labelled: Labelled, event: MakeEvent, log: Log
) -> None:
    _remover_first(signal, labelled, log)

    signal.publish(event(HandlingKind.LOADED))

    assert log == [
        ("remover", HandlingKind.LOADED),
        ("a", HandlingKind.LOADED),
        ("b", HandlingKind.LOADED),
    ]


def test_a_plain_list_skips_a_subscriber_when_one_unsubscribes_during_delivery(
    list_signal: _Form, labelled: Labelled, event: MakeEvent, log: Log
) -> None:
    _remover_first(list_signal, labelled, log)

    list_signal.publish(event(HandlingKind.LOADED))

    assert log == [("remover", HandlingKind.LOADED), ("b", HandlingKind.LOADED)]


def _history_behind_a_releaser(form: _Form, event: MakeEvent) -> TrackingHistory:
    """A releaser that publishes DELIVERED when it sees CLEARED, then a history, in that order."""

    def releaser(received: HandlingEvent, /) -> None:
        if received.kind is HandlingKind.CLEARED:
            form.publish(event(HandlingKind.DELIVERED))

    history = TrackingHistory()
    form.subscribe(releaser)
    form.subscribe(history.record)
    return history


def test_an_event_published_during_delivery_waits_its_turn(
    signal: Signal[HandlingEvent], event: MakeEvent
) -> None:
    history = _history_behind_a_releaser(signal, event)

    signal.publish(event(HandlingKind.CLEARED))

    assert [e.kind for e in history.events] == [HandlingKind.CLEARED, HandlingKind.DELIVERED]


def test_an_immediately_delivered_nested_event_arrives_out_of_order(
    list_signal: _Form, event: MakeEvent
) -> None:
    history = _history_behind_a_releaser(list_signal, event)

    list_signal.publish(event(HandlingKind.CLEARED))

    assert [e.kind for e in history.events] == [HandlingKind.DELIVERED, HandlingKind.CLEARED]
