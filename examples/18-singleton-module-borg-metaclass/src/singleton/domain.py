"""The tariff table as a frozen value, and the one error rating raises."""

from dataclasses import dataclass
from decimal import Decimal


class RatingError(LookupError):
    """A zone the tariff has no rate for."""


@dataclass(frozen=True, slots=True)
class TariffTable:
    """Per-kilogram rates by zone. Illustrative figures."""

    rates: frozendict[str, Decimal]

    def rate_for(self, zone: str) -> Decimal:
        try:
            return self.rates[zone]
        except KeyError:
            raise RatingError(f"no rate for zone {zone!r}") from None
