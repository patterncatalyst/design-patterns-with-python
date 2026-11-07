"""Money and the consignment identifier: the value types the billing code is built from."""

from dataclasses import dataclass
from decimal import Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)


@dataclass(frozen=True, slots=True)
class Money:
    """An amount in one currency. Adding or subtracting another currency raises ``ValueError``."""

    amount: Decimal
    currency: str = "EUR"

    def __add__(self, other: Money) -> Money:
        if other.currency != self.currency:
            raise ValueError(f"cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        if other.currency != self.currency:
            raise ValueError(f"cannot subtract {other.currency} from {self.currency}")
        return Money(self.amount - other.amount, self.currency)

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
