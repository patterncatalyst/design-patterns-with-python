"""The carrier feed as an async generator, and the session that closes it."""

import asyncio
from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest
from asyncio_patterns.domain import HandlingKind
from asyncio_patterns.feed import (
    InMemoryFeed,
    carrier_session,
    first_departure,
    handling_events,
)

if TYPE_CHECKING:
    from conftest import Runner

type FeedOf = Callable[..., InMemoryFeed]

KINDS = (HandlingKind.BOOKED, HandlingKind.LOADED, HandlingKind.DEPARTED, HandlingKind.DELIVERED)


def test_the_feed_yields_events_in_order_and_closes_at_the_end(
    run: Runner, feed_of: FeedOf
) -> None:
    feed = feed_of(*KINDS)

    async def main() -> list[HandlingKind]:
        return [event.kind async for event in handling_events(feed)]

    assert (run(main()), feed.closed) == (list(KINDS), True)


def test_breaking_out_of_async_for_leaves_the_feed_open(run: Runner, feed_of: FeedOf) -> None:
    feed = feed_of(*KINDS)

    async def main() -> list[bool]:
        events = handling_events(feed)
        async for _ in events:
            break
        open_after_break = not feed.closed
        await events.aclose()
        return [open_after_break, feed.closed]

    assert run(main()) == [True, True]


def test_first_departure_closes_the_feed_when_it_stops_early(run: Runner, feed_of: FeedOf) -> None:
    feed = feed_of(*KINDS)

    async def main() -> tuple[HandlingKind | None, bool]:
        event = await first_departure(feed)
        return (None if event is None else event.kind), feed.closed  # read before the loop ends

    assert run(main()) == (HandlingKind.DEPARTED, True)


def test_the_session_closes_the_feed_when_its_body_raises(run: Runner, feed_of: FeedOf) -> None:
    feed = feed_of(*KINDS)

    async def main() -> None:
        async with carrier_session(feed):
            raise LookupError("no such consignment")

    with pytest.raises(LookupError):
        run(main())

    assert feed.closed


def test_the_session_closes_the_feed_when_its_task_is_cancelled(
    run: Runner, feed_of: FeedOf
) -> None:
    feed = feed_of(*KINDS, stall=asyncio.Event())  # the event is never set, so the read waits

    async def main() -> bool:
        try:
            async with asyncio.timeout(0), carrier_session(feed) as session:
                await session.next_event()
        except TimeoutError:  # the guard's own TimeoutError is not caught here
            return True
        return False

    assert (run(main()), feed.closed) == (True, True)
