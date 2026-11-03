"""Command with undo: the part of the pattern that remains a design."""

from dataclasses import dataclass, field, replace

from three_way_split.domain import Consignment, Weight


@dataclass(slots=True)
class Booking:
    """A consignment under amendment, with the amendments applied so far."""

    consignment: Consignment
    applied: list[Amendment] = field(default_factory=list)

    def reweigh(self, weight: Weight) -> None:
        self.consignment = replace(self.consignment, weight=weight)

    def amend(self, amendment: Amendment) -> None:
        amendment.apply(self)
        self.applied.append(amendment)

    def undo_last(self) -> None:
        self.applied.pop().undo(self)


@dataclass(frozen=True, slots=True)
class Amendment:
    """A reweigh that remembers the weight it replaced, so it can be reversed."""

    before: Weight
    after: Weight

    def apply(self, booking: Booking) -> None:
        booking.reweigh(self.after)

    def undo(self, booking: Booking) -> None:
        booking.reweigh(self.before)
