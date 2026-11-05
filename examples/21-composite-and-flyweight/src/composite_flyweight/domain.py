"""Shipping values for the composite example: weight, commodity, consignment, consolidation."""

from dataclasses import dataclass
from decimal import Decimal
from functools import reduce
from typing import NewType, assert_never

ConsignmentId = NewType("ConsignmentId", str)


class ConsolidationError(ValueError):
    """A consolidation that cannot be built."""


@dataclass(frozen=True, slots=True)
class Weight:
    """A positive, finite mass in kilograms."""

    kilograms: Decimal

    def __post_init__(self) -> None:
        if not self.kilograms.is_finite() or self.kilograms <= 0:
            raise ValueError(f"weight must be positive and finite, got {self.kilograms}")

    def __add__(self, other: Weight) -> Weight:
        return Weight(self.kilograms + other.kilograms)


@dataclass(frozen=True, slots=True, weakref_slot=True)
class Commodity:
    """What is in a consignment, identified by its customs (HS) code.

    The weak-reference slot lets a pool hold commodities without keeping them alive.
    """

    hs_code: str
    description: str
    dangerous_goods: bool


@dataclass(frozen=True, slots=True)
class PortCall:
    """One stop on a route, numbered from 1."""

    port: str
    sequence: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """A leaf: one consignment with its commodity and ports."""

    id: ConsignmentId
    weight: Weight
    commodity: Commodity
    origin: str
    destination: str


@dataclass(frozen=True, slots=True)
class ConsolidatedShipment:
    """A group: consignments, or smaller consolidations, carried together.

    Built bottom-up, so its parts exist before it does and cannot be rewired afterwards.
    """

    id: str
    parts: tuple[Shipment, ...]

    def __post_init__(self) -> None:
        if not self.parts:
            raise ConsolidationError(f"consolidation {self.id} needs at least one part")
        seen: set[ConsignmentId] = set()
        for part in self.parts:
            for consignment_id in _consignment_ids(part):
                if consignment_id in seen:
                    raise ConsolidationError(
                        f"consignment {consignment_id} appears twice in consolidation {self.id}"
                    )
                seen.add(consignment_id)

    @property
    def weight(self) -> Weight:
        """The total, recursing through nested consolidations."""
        return reduce(Weight.__add__, (part.weight for part in self.parts))


type Shipment = Consignment | ConsolidatedShipment


def _consignment_ids(shipment: Shipment) -> tuple[ConsignmentId, ...]:
    match shipment:
        case Consignment():
            return (shipment.id,)
        case ConsolidatedShipment():
            return tuple(i for part in shipment.parts for i in _consignment_ids(part))
        case _ as unreachable:
            assert_never(unreachable)
