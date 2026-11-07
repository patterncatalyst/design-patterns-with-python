"""A carrier's live tracking feed as an async generator, and a session that closes it."""

import asyncio
from collections import deque
from collections.abc import AsyncGenerator, AsyncIterator, Iterable
from contextlib import aclosing, asynccontextmanager
from typing import Protocol

from asyncio_patterns.domain import HandlingEvent, HandlingKind


class CarrierFeed(Protocol):
    async def next_event(self) -> HandlingEvent | None: ...

    async def close(self) -> None: ...


class InMemoryFeed:
    """A stand-in for a carrier SDK's feed: no I/O, and it records whether it was closed.

    Given ``stall``, ``next_event`` waits on that event first, so a test can hold a reader
    inside the feed for as long as the event stays unset.
    """

    def __init__(
        self, events: Iterable[HandlingEvent], *, stall: asyncio.Event | None = None
    ) -> None:
        self._events = deque(events)
        self._stall = stall
        self.closed = False

    async def next_event(self) -> HandlingEvent | None:
        if self._stall is not None:
            await self._stall.wait()
        return self._events.popleft() if self._events else None

    async def close(self) -> None:
        self.closed = True


async def handling_events(feed: CarrierFeed) -> AsyncGenerator[HandlingEvent]:
    """Yield the feed's events until it ends, and close the feed when the generator closes.

    The annotation is ``AsyncGenerator`` because ``aclose`` is a method of that type and not of
    ``AsyncIterator``.
    """
    try:
        while (event := await feed.next_event()) is not None:
            yield event
    finally:
        await feed.close()


async def first_departure(feed: CarrierFeed) -> HandlingEvent | None:
    """Return the first departure, closing the feed even though the loop stops early."""
    async with aclosing(handling_events(feed)) as events:
        async for event in events:
            if event.kind is HandlingKind.DEPARTED:
                return event
    return None


@asynccontextmanager
async def carrier_session(feed: CarrierFeed) -> AsyncIterator[CarrierFeed]:
    """Hand the feed to the body and close it when the body ends, raises or is cancelled."""
    try:
        yield feed
    finally:
        await feed.close()
