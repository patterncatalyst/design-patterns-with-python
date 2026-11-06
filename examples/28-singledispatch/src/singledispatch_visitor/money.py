"""Rating area: an amount and its currency."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

_CENT = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class Money:
    """An amount and an ISO 4217 code."""

    amount: Decimal
    currency: str

    def times(self, days: int) -> Money:
        """Scale the amount by a number of days and round to cents."""
        return Money((days * self.amount).quantize(_CENT, rounding=ROUND_HALF_UP), self.currency)

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"
