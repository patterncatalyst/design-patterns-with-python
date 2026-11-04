"""Value types: compared by content, safe to share, usable as keys."""

import math
import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import NewType, Self

ConsignmentId = NewType("ConsignmentId", str)

_CURRENCY = re.compile(r"[A-Z]{3}")
_CENT = Decimal("0.01")


@dataclass(frozen=True, slots=True, order=True)
class Weight:
    """A positive mass in kilograms, ordered by its one field."""

    kilograms: float

    def __post_init__(self) -> None:
        if not (math.isfinite(self.kilograms) and self.kilograms > 0):
            raise ValueError(f"kilograms must be positive, got {self.kilograms}")


@dataclass(frozen=True, slots=True)
class Money:
    """An amount in whole cents and an ISO 4217 code. Unordered: ordering needs one currency."""

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not _CURRENCY.fullmatch(self.currency):
            raise ValueError(f"currency must be three capital letters, got {self.currency!r}")
        if self.amount != self.amount.quantize(_CENT):
            raise ValueError(f"amount must be whole cents, got {self.amount}")

    @classmethod
    def of(cls, amount: str, currency: str) -> Self:
        """Quantise to cents before construction, so validation only has to read."""
        return cls(Decimal(amount).quantize(_CENT, rounding=ROUND_HALF_UP), currency)

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise ValueError(f"cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)


@dataclass(frozen=True, slots=True, order=True)
class SlotId:
    """A stowage position, ordered by bay, then row, then tier."""

    bay: int
    row: int
    tier: int

    def __post_init__(self) -> None:
        if self.bay < 1:
            raise ValueError(f"bay must be at least 1, got {self.bay}")
        if self.row < 0:
            raise ValueError(f"row must be at least 0, got {self.row}")
        if self.tier < 1:
            raise ValueError(f"tier must be at least 1, got {self.tier}")
