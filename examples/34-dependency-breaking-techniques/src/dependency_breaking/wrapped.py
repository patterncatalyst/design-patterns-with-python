"""Wrap the API: the AIRCO SDK is wrapped into the shape FASTLINE already has.

``airco_quote`` takes a zone and a weight in kilograms and answers in euros, so both carriers
fit one ``CarrierQuoter`` type and the engine holds them as a mapping.
"""

from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal

from dependency_breaking import airco
from dependency_breaking.domain import Consignment, Money, RateQuote
from dependency_breaking.fastline import request_quote
from dependency_breaking.legacy import MARGIN
from dependency_breaking.parameterised import AircoPrice

type CarrierQuoter = Callable[[str, Decimal], Decimal]


def airco_quote(zone: str, weight_kg: Decimal, /, *, price: AircoPrice = airco.price) -> Decimal:
    """Price a consignment with AIRCO, in euros. Grams are truncated, as they always were."""
    cents = price(destination=zone, grams=int(weight_kg * 1000))
    return Decimal(cents) / 100


class RateEngine:
    """Quote a consignment with the cheaper of two carriers, plus a margin."""

    def __init__(
        self,
        *,
        fastline: CarrierQuoter = request_quote,
        airco: CarrierQuoter = airco_quote,
        margin: Decimal = MARGIN,
    ) -> None:
        self._quoters: dict[str, CarrierQuoter] = {"AIRCO": airco, "FASTLINE": fastline}
        self._margin = margin

    def quote(self, consignment: Consignment) -> RateQuote:
        prices = {
            code: quoter(consignment.zone, consignment.weight_kg)
            for code, quoter in self._quoters.items()
        }
        code, cheapest = min(prices.items(), key=lambda item: (item[1], item[0]))
        total = (cheapest * self._margin).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return RateQuote(consignment.id, code, Money(total))
