"""The async Observer: every subscriber runs, and the failures leave together."""

import asyncio
from collections.abc import Callable
from typing import TYPE_CHECKING

from asyncio_patterns.domain import ConsignmentId, HandlingEvent, HandlingKind
from asyncio_patterns.signal import AsyncSignal

if TYPE_CHECKING:
    from conftest import FailingSubscriber, GatedSubscriber, Runner

    type SignalFactory = Callable[[], AsyncSignal[HandlingEvent]]
    type GatedOf = Callable[[str, list[str], asyncio.Event], GatedSubscriber]
    type FailingOf = Callable[[asyncio.Event], FailingSubscriber]

EVENTS = [
    HandlingEvent(ConsignmentId("CN-1"), HandlingKind.BOOKED, "NLRTM"),
    HandlingEvent(ConsignmentId("CN-1"), HandlingKind.LOADED, "NLRTM"),
    HandlingEvent(ConsignmentId("CN-1"), HandlingKind.DEPARTED, "NLRTM"),
]


def test_every_subscriber_hears_each_event_in_subscription_order(
    run: Runner, publish_form: SignalFactory, gated_subscriber: GatedOf
) -> None:
    """The order within one publish is the order the loop starts the tasks, which is first in,
    first out in CPython and not a documented guarantee."""
    log: list[str] = []
    open_gate = asyncio.Event()
    open_gate.set()
    signal = publish_form()
    signal.subscribe(gated_subscriber("first", log, open_gate))
    signal.subscribe(gated_subscriber("second", log, open_gate))

    async def main() -> None:
        for event in EVENTS:
            await signal.publish(event)

    run(main())

    assert log == [f"{name} {event.kind.name}" for event in EVENTS for name in ("first", "second")]


def test_a_failing_subscriber_does_not_stop_the_others(
    run: Runner, gated_subscriber: GatedOf, failing_subscriber: FailingOf
) -> None:
    log: list[str] = []
    gate, failed = asyncio.Event(), asyncio.Event()
    signal = AsyncSignal[HandlingEvent]()
    signal.subscribe(gated_subscriber("history", log, gate))
    signal.subscribe(failing_subscriber(failed))

    async def main() -> list[str]:
        publishing = asyncio.create_task(signal.publish(EVENTS[0]))
        await failed.wait()
        gate.set()  # the failure has happened, and the gated subscriber has not yet finished
        failures: list[str] = []
        try:
            await publishing
        except ExceptionGroup as group:
            failures.extend(str(error) for error in group.exceptions)
        return failures

    assert (run(main()), log) == (["history full"], ["history BOOKED"])


def test_a_task_group_publisher_cancels_the_other_subscribers_when_one_fails(
    run: Runner,
    taskgroup_signal: SignalFactory,
    gated_subscriber: GatedOf,
    failing_subscriber: FailingOf,
) -> None:
    log: list[str] = []
    signal = taskgroup_signal()
    signal.subscribe(gated_subscriber("history", log, asyncio.Event()))  # the gate never opens
    signal.subscribe(failing_subscriber(asyncio.Event()))

    async def main() -> list[str]:
        failures: list[str] = []
        try:
            await signal.publish(EVENTS[0])
        except ExceptionGroup as group:
            failures.extend(str(error) for error in group.exceptions)
        return failures

    assert (run(main()), log) == (["history full"], [])


def test_an_unsubscribed_subscriber_hears_nothing(
    run: Runner, publish_form: SignalFactory, gated_subscriber: GatedOf
) -> None:
    log: list[str] = []
    open_gate = asyncio.Event()
    open_gate.set()
    signal = publish_form()
    unsubscribe = signal.subscribe(gated_subscriber("leaver", log, open_gate))
    signal.subscribe(gated_subscriber("stayer", log, open_gate))
    unsubscribe()

    run(signal.publish(EVENTS[0]))

    assert log == ["stayer BOOKED"]
