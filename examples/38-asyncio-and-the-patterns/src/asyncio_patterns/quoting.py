"""Quoting a consignment with several carriers at once."""

import asyncio
import threading
from collections.abc import Sequence
from decimal import Decimal
from typing import Protocol

from asyncio_patterns.domain import CarrierTimeoutError, Consignment, Money, RateQuote

FASTLINE = "FASTLINE"
AIRCO = "AIRCO"


class RateSource(Protocol):
    async def quote(self, consignment: Consignment, /) -> RateQuote: ...


def _euros(cents: int) -> Money:
    return Money(Decimal(cents).scaleb(-2))


class FastlineSource:
    """An asynchronous stand-in for FASTLINE's API. Prices are illustrative."""

    async def quote(self, consignment: Consignment, /) -> RateQuote:
        return RateQuote(consignment.id, FASTLINE, _euros(700 + 25 * int(consignment.weight_kg)))


class AircoClient:
    """A blocking stand-in for AIRCO's SDK. Prices are illustrative.

    Given ``ready``, ``price`` blocks its calling thread until that event is set, or raises
    ``CarrierTimeoutError`` after ``patience`` seconds. A test sets the event from the event
    loop, which only works if the call runs in another thread.
    """

    def __init__(self, *, ready: threading.Event | None = None, patience: float = 10.0) -> None:
        self._ready = ready
        self._patience = patience

    def price(self, *, destination: str, grams: int) -> int:
        """Return the price in cents."""
        if self._ready is not None and not self._ready.wait(self._patience):
            raise CarrierTimeoutError(f"AIRCO did not answer for {destination}")
        return 500 + grams // 100


class AircoSource:
    """Adapt the blocking SDK to ``RateSource`` by running each call in a worker thread."""

    def __init__(self, client: AircoClient) -> None:
        self._client = client

    async def quote(self, consignment: Consignment, /) -> RateQuote:
        cents = await asyncio.to_thread(
            self._client.price,
            destination=consignment.zone,
            grams=int(consignment.weight_kg * 1000),
        )
        return RateQuote(consignment.id, AIRCO, _euros(cents))


async def cheapest(
    consignment: Consignment,
    /,
    sources: Sequence[RateSource],
    *,
    within: float | None = None,
) -> RateQuote:
    """Ask every source at once and return the lowest total.

    A source that fails cancels the others and the failure leaves as an ``ExceptionGroup``.
    ``within`` bounds the whole group in seconds, and ``None`` sets no bound.
    """
    async with asyncio.timeout(within):
        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(source.quote(consignment)) for source in sources]
    return min((task.result() for task in tasks), key=lambda quote: quote.total.amount)


async def first_quote(consignment: Consignment, /, sources: Sequence[RateSource]) -> RateQuote:
    """Return the first answer and cancel the sources still waiting."""
    answers: list[RateQuote] = []

    async with asyncio.TaskGroup() as group:

        async def ask(source: RateSource) -> None:
            answers.append(await source.quote(consignment))
            group.cancel()

        for source in sources:
            group.create_task(ask(source))
    return answers[0]
