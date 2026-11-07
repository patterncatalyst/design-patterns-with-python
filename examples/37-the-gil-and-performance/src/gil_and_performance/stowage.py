"""A sailing's stowage plan: the shared state that two bookings reserve slots on."""

from collections.abc import Callable, Mapping
from contextlib import AbstractContextManager
from threading import Lock
from types import MappingProxyType

from gil_and_performance.domain import ConsignmentId, SlotId


def _no_gap() -> None:
    """The default gap: nothing happens between picking a slot and storing it."""


class StowagePlan:
    """A Monitor Object: one lock guards the read and the write of the reservations.

    ``gap`` is a test seam. It runs between picking a slot and storing it, which is where a
    test parks a thread to force an interleaving.
    """

    def __init__(
        self,
        sailing: str,
        *,
        lock: AbstractContextManager[object] | None = None,
        gap: Callable[[], object] = _no_gap,
    ) -> None:
        self.sailing = sailing
        self._lock = Lock() if lock is None else lock
        self._gap = gap
        self._reservations: dict[SlotId, ConsignmentId] = {}

    @property
    def reservations(self) -> Mapping[SlotId, ConsignmentId]:
        """A read-only view of who holds each slot."""
        return MappingProxyType(self._reservations)

    def reserve(self, consignment_id: ConsignmentId) -> SlotId:
        with self._lock:
            slot = SlotId(1, 1, len(self._reservations) + 1)
            self._gap()
            self._reservations[slot] = consignment_id
        return slot
