"""Rating area: a surcharge per container kind, dispatched as a method.

Rates are illustrative. Container numbers in the tests are placeholders: real owner prefixes
belong to real companies.
"""

from dataclasses import dataclass
from decimal import Decimal
from functools import singledispatchmethod

from singledispatch_visitor.money import Money


@dataclass(frozen=True, slots=True)
class DryContainer:
    number: str


@dataclass(frozen=True, slots=True)
class ReeferContainer:
    number: str
    set_point_c: Decimal


@dataclass(frozen=True, slots=True)
class TankContainer:
    number: str


class SurchargeError(LookupError):
    """A container kind with no surcharge rule."""


@dataclass(frozen=True, slots=True)
class SurchargeSchedule:
    reefer_per_day: Money
    tank_cleaning: Money

    @singledispatchmethod
    def surcharge(self, container: object, days: int) -> Money:
        raise SurchargeError(f"no surcharge rule for {type(container).__name__}")

    @surcharge.register
    def _dry(self, container: DryContainer, days: int) -> Money:
        return Money(Decimal("0.00"), self.reefer_per_day.currency)

    @surcharge.register
    def _reefer(self, container: ReeferContainer, days: int) -> Money:
        return self.reefer_per_day.times(days)

    @surcharge.register
    def _tank(self, container: TankContainer, days: int) -> Money:
        return self.tank_cleaning
