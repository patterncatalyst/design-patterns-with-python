"""An asynchronous Observer: every subscriber runs, then the failures are raised together."""

import asyncio
from collections.abc import Awaitable, Callable

type Subscriber[E] = Callable[[E], Awaitable[None]]
type Unsubscribe = Callable[[], None]


class AsyncSignal[E]:
    """Publish an event to async subscribers on one event loop.

    ``publish`` starts every subscriber, waits for all of them, and then raises one
    ``ExceptionGroup`` of the failures, so a failing subscriber does not stop the others.
    """

    def __init__(self) -> None:
        self._subscribers: list[Subscriber[E]] = []

    def subscribe(self, subscriber: Subscriber[E], /) -> Unsubscribe:
        self._subscribers.append(subscriber)
        return lambda: self._subscribers.remove(subscriber)

    async def publish(self, event: E, /) -> None:
        results = await asyncio.gather(
            *(subscriber(event) for subscriber in self._subscribers), return_exceptions=True
        )
        failures = [result for result in results if isinstance(result, BaseException)]
        if failures:
            raise BaseExceptionGroup(f"{len(failures)} subscriber(s) failed", failures)
