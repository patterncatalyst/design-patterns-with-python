"""Value types for the rating examples."""

from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


@dataclass(frozen=True, slots=True)
class Weight:
    """A positive mass in kilograms."""

    kilograms: Decimal

    def __post_init__(self) -> None:
        if self.kilograms <= 0:
            raise ValueError(f"weight must be positive, got {self.kilograms}")


@dataclass(frozen=True, slots=True)
class Consignment:
    id: ConsignmentId
    zone: str
    weight: Weight
