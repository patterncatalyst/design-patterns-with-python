"""Stowage: a plan has identity and a lifecycle, so it is an entity and not a value."""

from dataclasses import dataclass, field

from value_semantics.values import ConsignmentId, SlotId


@dataclass(eq=False, slots=True)
class StowagePlan:
    """Slot reservations for one sailing. Equality and hash stay identity based."""

    sailing: str
    reservations: dict[SlotId, ConsignmentId] = field(default_factory=dict)

    def reserve(self, slot: SlotId, consignment_id: ConsignmentId) -> None:
        if slot in self.reservations:
            raise ValueError(f"slot {slot} already holds {self.reservations[slot]}")
        self.reservations[slot] = consignment_id

    def occupied(self) -> list[SlotId]:
        return sorted(self.reservations)
