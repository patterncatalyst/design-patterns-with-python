"""Fixtures: a guarded runner, feeds, test doubles for carriers and subscribers, and the one
comparison form of the signal.

Tests wait on events, barriers, queues and joins (one test yields once with ``sleep(0)``), under a
ten-second guard that a healthy run never reaches.
"""

import asyncio
from collections.abc import Callable, Coroutine
from decimal import Decimal
from typing import TYPE_CHECKING, override

import pytest
from asyncio_patterns.domain import (
    CarrierTimeoutError,
    ConsignmentId,
    HandlingEvent,
    HandlingKind,
    Money,
    RateQuote,
)
from asyncio_patterns.feed import InMemoryFeed
from asyncio_patterns.signal import AsyncSignal, Subscriber

if TYPE_CHECKING:
    from asyncio_patterns.domain import Consignment

GUARD_SECONDS = 10


class Runner:
    """Run a coroutine on a fresh event loop under the guard."""

    def __call__[T](self, coroutine: Coroutine[object, object, T]) -> T:
        async def guarded() -> T:
            async with asyncio.timeout(GUARD_SECONDS):
                return await coroutine

        return asyncio.run(guarded())


@pytest.fixture
def run() -> Runner:
    return Runner()


@pytest.fixture
def feed_of() -> Callable[..., InMemoryFeed]:
    """Build a feed of events of the given kinds for one consignment."""

    def build(*kinds: HandlingKind, stall: asyncio.Event | None = None) -> InMemoryFeed:
        events = [HandlingEvent(ConsignmentId("CN-1"), kind, "NLRTM") for kind in kinds]
        return InMemoryFeed(events, stall=stall)

    return build


class WaitingSource:
    """A carrier that never answers, and logs when it is cancelled."""

    def __init__(self, carrier: str, log: list[str], started: asyncio.Event) -> None:
        self._carrier = carrier
        self._log = log
        self._started = started

    async def quote(self, consignment: Consignment, /) -> RateQuote:
        self._started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            self._log.append(f"{self._carrier} cancelled")
            raise
        raise AssertionError("a waiting source was released")


class AnswersAfter:
    """A carrier that answers once ``started`` is set."""

    def __init__(self, carrier: str, started: asyncio.Event) -> None:
        self._carrier = carrier
        self._started = started

    async def quote(self, consignment: Consignment, /) -> RateQuote:
        await self._started.wait()
        return RateQuote(consignment.id, self._carrier, Money(Decimal("1.00")))


class FailsAfter:
    """A carrier that times out once ``started`` is set."""

    def __init__(self, started: asyncio.Event) -> None:
        self._started = started

    async def quote(self, consignment: Consignment, /) -> RateQuote:
        await self._started.wait()
        raise CarrierTimeoutError("FASTLINE did not answer")


@pytest.fixture
def waiting_source() -> Callable[[str, list[str], asyncio.Event], WaitingSource]:
    return WaitingSource


@pytest.fixture
def answers_after() -> Callable[[str, asyncio.Event], AnswersAfter]:
    return AnswersAfter


@pytest.fixture
def fails_after() -> Callable[[asyncio.Event], FailsAfter]:
    return FailsAfter


class GatedSubscriber:
    """Records ``<name> <kind>`` once its gate opens."""

    def __init__(self, name: str, log: list[str], gate: asyncio.Event) -> None:
        self._name = name
        self._log = log
        self._gate = gate

    async def __call__(self, event: HandlingEvent, /) -> None:
        await self._gate.wait()
        self._log.append(f"{self._name} {event.kind.name}")


class FailingSubscriber:
    """Sets ``failed`` and then raises."""

    def __init__(self, failed: asyncio.Event) -> None:
        self._failed = failed

    async def __call__(self, event: HandlingEvent, /) -> None:
        self._failed.set()
        raise LookupError("history full")


@pytest.fixture
def gated_subscriber() -> Callable[[str, list[str], asyncio.Event], GatedSubscriber]:
    return GatedSubscriber


@pytest.fixture
def failing_subscriber() -> Callable[[asyncio.Event], FailingSubscriber]:
    return FailingSubscriber


async def _deliver[E](subscriber: Subscriber[E], event: E) -> None:
    await subscriber(event)


class _TaskGroupSignal[E](AsyncSignal[E]):
    """The comparison form: publish in a task group, so one failure cancels the rest."""

    @override
    async def publish(self, event: E, /) -> None:
        async with asyncio.TaskGroup() as group:
            for subscriber in self._subscribers:
                group.create_task(_deliver(subscriber, event))


@pytest.fixture
def taskgroup_signal() -> Callable[[], AsyncSignal[HandlingEvent]]:
    return _TaskGroupSignal


@pytest.fixture(params=["gather", "taskgroup"])
def publish_form(request: pytest.FixtureRequest) -> Callable[[], AsyncSignal[HandlingEvent]]:
    """The two publishers on one table of cases: ``gather`` is the signal in src."""
    if request.param == "gather":
        return AsyncSignal
    return _TaskGroupSignal
