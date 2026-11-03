"""asyncio and the patterns: async iteration, async context managers, coroutine commands.

Every ordering below is forced with ``asyncio.Event`` and ``asyncio.sleep(0)`` (a bare yield to
the event loop), never with wall-clock delays.
"""

import asyncio
import contextlib
from collections.abc import AsyncGenerator, AsyncIterator
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class TrackingEvent:
    shipment_id: str
    status: str


@dataclass
class FakeCarrierFeed:
    """A carrier's tracking feed that records whether it was opened and closed."""

    events: list[TrackingEvent]
    opened: bool = False
    closed: bool = False
    pulled: int = 0

    async def open(self) -> None:
        await asyncio.sleep(0)
        self.opened = True

    async def close(self) -> None:
        await asyncio.sleep(0)
        self.closed = True


async def tracking_events(feed: FakeCarrierFeed) -> AsyncGenerator[TrackingEvent]:
    """Iterator pattern as an async generator: pull-based, suspended between events."""
    await feed.open()
    try:
        for event in feed.events:
            await asyncio.sleep(0)
            feed.pulled += 1
            yield event
    finally:
        await feed.close()


@contextlib.asynccontextmanager
async def carrier_session(feed: FakeCarrierFeed) -> AsyncIterator[FakeCarrierFeed]:
    """Context-manager pattern, async: the feed is closed on success, error and cancellation."""
    await feed.open()
    try:
        yield feed
    finally:
        await feed.close()


async def collect_statuses(feed: FakeCarrierFeed, limit: int) -> list[str]:
    """Take at most ``limit`` statuses; ``aclosing`` runs the generator's cleanup on early exit."""
    statuses: list[str] = []
    async with contextlib.aclosing(tracking_events(feed)) as events:
        async for event in events:
            statuses.append(event.status)
            if len(statuses) == limit:
                break
    return statuses


# --- Command as a coroutine -------------------------------------------------------------


@dataclass
class Shipment:
    shipment_id: str
    carrier: str


class Command(Protocol):
    async def execute(self) -> None: ...
    async def undo(self) -> None: ...


@dataclass
class ReassignCarrier:
    shipment: Shipment
    new_carrier: str
    _previous: str | None = field(default=None, init=False)

    async def execute(self) -> None:
        await asyncio.sleep(0)
        self._previous = self.shipment.carrier
        self.shipment.carrier = self.new_carrier

    async def undo(self) -> None:
        await asyncio.sleep(0)
        if self._previous is not None:
            self.shipment.carrier = self._previous


@dataclass
class FailingCommand:
    async def execute(self) -> None:
        await asyncio.sleep(0)
        msg = "carrier rejected the change"
        raise RuntimeError(msg)

    async def undo(self) -> None:
        return None


class CommandWorker:
    """Executes queued commands in order and keeps a history for undo."""

    def __init__(self) -> None:
        self.queue: asyncio.Queue[Command | None] = asyncio.Queue()
        self.history: list[Command] = []
        self.errors: list[Exception] = []

    async def run(self) -> None:
        """Drain the queue until the ``None`` sentinel."""
        while (command := await self.queue.get()) is not None:
            try:
                await command.execute()
            except Exception as error:
                self.errors.append(error)
            else:
                self.history.append(command)
            finally:
                self.queue.task_done()
        self.queue.task_done()

    async def undo_all(self) -> None:
        while self.history:
            await self.history.pop().undo()


# --- ordering primitives ----------------------------------------------------------------


async def interleave_with_sleep0(rounds: int) -> list[str]:
    """Two tasks that yield with ``sleep(0)`` after every step alternate in a fixed order."""
    log: list[str] = []

    async def step(name: str) -> None:
        for i in range(1, rounds + 1):
            log.append(f"{name}{i}")
            await asyncio.sleep(0)

    async with asyncio.TaskGroup() as group:
        group.create_task(step("a"))
        group.create_task(step("b"))
    return log


async def gather_order(finish_order: list[str]) -> tuple[list[str], list[str]]:
    """``gather`` returns results in argument order, whatever order the awaitables finish in.

    Returns ``(results, completion_order)``. Each job waits for its own gate; gates are opened
    in ``finish_order``.
    """
    names = sorted(finish_order)
    gates = {name: asyncio.Event() for name in names}
    completed: list[str] = []

    async def job(name: str) -> str:
        await gates[name].wait()
        completed.append(name)
        return name.upper()

    async def open_gates() -> None:
        for name in finish_order:
            gates[name].set()
            for _ in range(3):  # let the job that was just released run to completion
                await asyncio.sleep(0)

    results, _ = await asyncio.gather(asyncio.gather(*(job(name) for name in names)), open_gates())
    return results, completed


async def first_failure_cancels_siblings() -> tuple[list[str], bool]:
    """``TaskGroup``: the first failure cancels the other tasks and surfaces as an ExceptionGroup.

    Returns ``(error messages, sibling_was_cancelled)``.
    """
    never = asyncio.Event()
    cancelled = False

    async def sibling() -> None:
        nonlocal cancelled
        try:
            await never.wait()
        except asyncio.CancelledError:
            cancelled = True
            raise

    async def failing() -> None:
        await asyncio.sleep(0)
        msg = "carrier feed dropped"
        raise ConnectionError(msg)

    messages: list[str] = []
    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(sibling())
            group.create_task(failing())
    except* ConnectionError as group_error:
        messages = [str(error) for error in group_error.exceptions]
    return messages, cancelled


async def wait_for_never_set_event() -> bool:
    """Cancellation without a clock dependency: a zero deadline expires at the next yield.

    The event is never set, so the only way out is the timeout. Returns True when it fired.
    """
    never = asyncio.Event()
    try:
        async with asyncio.timeout(0):
            await never.wait()
    except TimeoutError:
        return True
    return False


async def lost_update_across_await(workers: int) -> int:
    """The asyncio version of the lost update: an ``await`` between read and write.

    With no ``await`` in the gap a coroutine cannot be interrupted; with one, every worker reads
    the same value. Deterministic, because ``sleep(0)`` hands control to the other tasks.
    """
    count = 0

    async def bump() -> None:
        nonlocal count
        current = count
        await asyncio.sleep(0)
        count = current + 1

    async with asyncio.TaskGroup() as group:
        for _ in range(workers):
            group.create_task(bump())
    return count


async def no_await_no_race(workers: int) -> int:
    """The same increments without an ``await`` in the gap: no lock needed, none lost."""
    count = 0

    async def bump() -> None:
        nonlocal count
        count += 1
        await asyncio.sleep(0)

    async with asyncio.TaskGroup() as group:
        for _ in range(workers):
            group.create_task(bump())
    return count


async def locked_across_await(workers: int) -> int:
    """With an ``await`` in the gap, an ``asyncio.Lock`` restores correctness."""
    count = 0
    lock = asyncio.Lock()

    async def bump() -> None:
        nonlocal count
        async with lock:
            current = count
            await asyncio.sleep(0)
            count = current + 1

    async with asyncio.TaskGroup() as group:
        for _ in range(workers):
            group.create_task(bump())
    return count
