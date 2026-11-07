"""Coroutine commands on a queue, drained by one worker until the queue is shut down."""

import asyncio
from collections.abc import Awaitable, Callable

type BookingCommand = Callable[[], Awaitable[str]]


async def run_commands(queue: asyncio.Queue[BookingCommand], log: list[str]) -> None:
    """Run each queued command in order and log its result or its failure.

    The worker is an Active Object: callers enqueue and the worker executes. It stops when the
    queue is shut down and empty, and logs ``worker stopped``.
    """
    while True:
        try:
            command = await queue.get()
        except asyncio.QueueShutDown:
            log.append("worker stopped")
            return
        try:
            log.append(await command())
        except Exception as error:
            log.append(f"failed: {error}")
        finally:
            queue.task_done()
