"""Routing: a sailing's slots, reserved lowest tier first and released by slot."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol

from final_project.domain import ConsignmentId, Sailing


@dataclass(frozen=True, slots=True, order=True)
class SlotId:
    bay: int
    row: int
    tier: int


class StowageFullError(Exception):
    """Every tier on the sailing is taken."""


class SlotPlan(Protocol):
    """What the booking desk needs from a stowage plan."""

    @property
    def sailing(self) -> Sailing: ...

    def reserve(self, consignment_id: ConsignmentId, /) -> SlotId: ...

    def release(self, slot: SlotId, /) -> None: ...


class StowagePlan:
    def __init__(self, sailing: Sailing, *, tiers: int) -> None:
        self.sailing = sailing
        self._tiers = tiers
        self._reservations: dict[SlotId, ConsignmentId] = {}

    @property
    def reservations(self) -> Mapping[SlotId, ConsignmentId]:
        """A read-only view of who holds each slot."""
        return MappingProxyType(self._reservations)

    def reserve(self, consignment_id: ConsignmentId, /) -> SlotId:
        for tier in range(1, self._tiers + 1):
            slot = SlotId(1, 1, tier)
            if slot not in self._reservations:
                self._reservations[slot] = consignment_id
                return slot
        raise StowageFullError(f"sailing {self.sailing.code} has no free tier")

    def release(self, slot: SlotId, /) -> None:
        del self._reservations[slot]
