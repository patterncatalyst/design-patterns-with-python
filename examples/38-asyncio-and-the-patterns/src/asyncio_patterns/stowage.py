"""A sailing's stowage plan for tasks on one event loop: an await is where another task runs."""

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from contextlib import AbstractAsyncContextManager
from types import MappingProxyType

from asyncio_patterns.domain import ConsignmentId, SlotId


class StowagePlan:
    """Reserve slots for tasks on one event loop.

    ``reserve`` picks a slot, awaits ``confirm`` and stores the reservation, all under ``lock``.
    By default the lock is a fresh ``asyncio.Lock``. A test passes ``contextlib.nullcontext()``
    to run without one, which shows the double booking an await allows.
    """

    def __init__(
        self, sailing: str, *, lock: AbstractAsyncContextManager[object] | None = None
    ) -> None:
        self.sailing = sailing
        self._lock = asyncio.Lock() if lock is None else lock
        self._reservations: dict[SlotId, ConsignmentId] = {}

    @property
    def reservations(self) -> Mapping[SlotId, ConsignmentId]:
        """Who holds each slot."""
        return MappingProxyType(self._reservations)

    async def reserve(
        self, consignment_id: ConsignmentId, confirm: Callable[[], Awaitable[object]]
    ) -> SlotId:
        async with self._lock:
            slot = SlotId(1, 1, len(self._reservations) + 1)
            await confirm()
            self._reservations[slot] = consignment_id
        return slot
