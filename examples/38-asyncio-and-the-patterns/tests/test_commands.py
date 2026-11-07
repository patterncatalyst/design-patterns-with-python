"""Coroutine commands on a queue, and the worker that drains it until the queue shuts down."""

import asyncio
from typing import TYPE_CHECKING

import pytest
from asyncio_patterns.commands import BookingCommand, run_commands

if TYPE_CHECKING:
    from conftest import Runner


def _books(consignment: str) -> BookingCommand:
    async def command() -> str:
        return f"booked {consignment}"

    return command


def _redirects(consignment: str) -> BookingCommand:
    async def command() -> str:
        return f"redirected {consignment}"

    return command


async def _no_slot() -> str:
    raise LookupError("no slot")


def test_queued_commands_run_in_order_and_a_failure_is_recorded(run: Runner) -> None:
    log: list[str] = []

    async def main() -> None:
        queue = asyncio.Queue[BookingCommand]()
        worker = asyncio.create_task(run_commands(queue, log))
        for command in (_books("CN-1"), _no_slot, _redirects("CN-1")):
            queue.put_nowait(command)
        await queue.join()
        queue.shutdown()
        await worker

    run(main())

    assert log == ["booked CN-1", "failed: no slot", "redirected CN-1", "worker stopped"]


def test_shutdown_lets_the_worker_drain_the_queue_then_stop(run: Runner) -> None:
    log: list[str] = []

    async def main() -> None:
        queue = asyncio.Queue[BookingCommand]()
        for command in (_books("CN-1"), _no_slot, _books("CN-2")):
            queue.put_nowait(command)
        queue.shutdown()
        await run_commands(queue, log)
        await queue.join()

    run(main())

    assert log == ["booked CN-1", "failed: no slot", "booked CN-2", "worker stopped"]


def test_an_immediate_shutdown_drops_the_pending_commands(run: Runner) -> None:
    log: list[str] = []

    async def main() -> int:
        queue = asyncio.Queue[BookingCommand]()
        for command in (_books("CN-1"), _books("CN-2")):
            queue.put_nowait(command)
        queue.shutdown(immediate=True)
        await run_commands(queue, log)
        await queue.join()
        return queue.qsize()

    assert (run(main()), log) == (0, ["worker stopped"])


def test_a_shut_down_queue_refuses_a_new_command(run: Runner) -> None:
    log: list[str] = []

    async def main() -> None:
        queue = asyncio.Queue[BookingCommand]()
        worker = asyncio.create_task(run_commands(queue, log))
        queue.shutdown()
        await worker
        queue.put_nowait(_books("CN-3"))

    with pytest.raises(asyncio.QueueShutDown):
        run(main())

    assert log == ["worker stopped"]
