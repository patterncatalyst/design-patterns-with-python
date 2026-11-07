"""A coroutine that never awaits holds the event loop."""

import asyncio
from decimal import Decimal

from gil_and_performance.domain import Consignment, ConsignmentId
from gil_and_performance.rating import quote

GUARD_SECONDS = 10


def test_a_coroutine_that_never_awaits_holds_the_loop_until_it_returns() -> None:
    log: list[str] = []
    started = asyncio.Event()
    consignment = Consignment(ConsignmentId("CN-1"), "EU", Decimal("50"))

    async def rating() -> None:
        log.append("rating started")
        started.set()
        quote(consignment)  # CPU-bound and never awaits, so nothing else can run
        log.append("rating finished")

    async def tracking() -> None:
        await started.wait()
        log.append("tracking polled")

    async def main() -> None:
        async with asyncio.timeout(GUARD_SECONDS):
            await asyncio.gather(rating(), tracking())

    asyncio.run(main())

    assert log == ["rating started", "rating finished", "tracking polled"]
