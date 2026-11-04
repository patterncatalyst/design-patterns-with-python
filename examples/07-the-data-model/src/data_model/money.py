"""Money and the rate quote built from it."""

import functools
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import NewType

ConsignmentId = NewType("ConsignmentId", str)

_CENT = Decimal("0.01")


@functools.total_ordering
@dataclass(frozen=True, slots=True)
class Money:
    """An amount in one currency. Arithmetic and ordering are defined within a currency."""

    amount: Decimal
    currency: str

    def __add__(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f"cannot add {other.currency} to {self.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: Decimal | int) -> Money:
        if not isinstance(factor, Decimal | int):
            return NotImplemented
        return Money((self.amount * factor).quantize(_CENT, rounding=ROUND_HALF_UP), self.currency)

    def __rmul__(self, factor: Decimal | int) -> Money:
        return self.__mul__(factor)

    def __lt__(self, other: Money) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f"cannot compare {self.currency} with {other.currency}")
        return self.amount < other.amount

    def __str__(self) -> str:
        return f"{self.currency} {self.amount}"

    def __format__(self, spec: str) -> str:
        return format(str(self), spec)


@dataclass(frozen=True, slots=True)
class RateQuote:
    """A priced consignment: net charge plus tax. Quotes have no natural order."""

    consignment_id: ConsignmentId
    net: Money
    tax: Money

    @property
    def total(self) -> Money:
        return self.net + self.tax
