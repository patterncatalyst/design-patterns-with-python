"""The rewrite: a tariff as data, and a quote that finds the band by bisection."""

from bisect import bisect_left
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from refactor_or_rewrite.domain import MARGIN, Consignment, Money, RateQuote, RatingError


@dataclass(frozen=True, slots=True)
class Tariff:
    """Ascending inclusive upper limits in kilograms, and one price per band for each zone."""

    upper_kg: tuple[Decimal, ...]
    prices: Mapping[str, tuple[Decimal, ...]]


STANDARD_TARIFF = Tariff(
    upper_kg=(Decimal(5), Decimal(20), Decimal(50)),
    prices=frozendict(
        {
            "EU": (Decimal("12.00"), Decimal("25.00"), Decimal("48.00")),
            "ASIA": (Decimal("30.00"), Decimal("55.00"), Decimal("98.00")),
        }
    ),
)


def quote(consignment: Consignment, /, *, tariff: Tariff = STANDARD_TARIFF) -> RateQuote:
    """Price a consignment from the tariff. An unknown zone is refused."""
    try:
        band_prices = tariff.prices[consignment.zone]
    except KeyError:
        raise RatingError(f"no tariff for zone {consignment.zone!r}") from None
    kg = consignment.weight.kilograms
    # bisect_left keeps each limit inclusive: a weight equal to a limit stays in its band.
    band = bisect_left(tariff.upper_kg, kg)
    if band == len(tariff.upper_kg):
        raise RatingError(f"no band for {kg} kg")
    total = (band_prices[band] * MARGIN).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return RateQuote(consignment.id, Money(total))
