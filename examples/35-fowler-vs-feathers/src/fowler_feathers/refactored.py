"""The legacy engine after three catalogue refactorings, with the same constructor.

- Replace Magic Literal: ``CENT`` names the quantum the total is rounded to.
- Extract Function: ``_cheapest`` and ``_with_margin`` hold the choice and the margin that
  ``quote`` used to do inline.
- Replace Primitive with Object: carrier prices are ``Money``, kept at full precision. Only the
  total is rounded, once, half up.
"""

from collections.abc import Mapping
from decimal import ROUND_HALF_UP, Decimal

from fowler_feathers import airco
from fowler_feathers.domain import Consignment, Money, RateQuote
from fowler_feathers.fastline import request_quote
from fowler_feathers.legacy import MARGIN, AircoPrice, FastlineQuote

CENT = Decimal("0.01")


def _cheapest(prices: Mapping[str, Money]) -> tuple[str, Money]:
    """The carrier with the lowest price."""
    return min(prices.items(), key=lambda item: (item[1].amount, item[0]))


class RateEngine:
    """Quote a consignment with the cheaper of two carriers, plus a margin."""

    def __init__(
        self,
        *,
        fastline_quote: FastlineQuote = request_quote,
        airco_price: AircoPrice = airco.price,
        margin: Decimal = MARGIN,
    ) -> None:
        self._fastline_quote = fastline_quote
        self._airco_price = airco_price
        self._margin = margin

    def _prices(self, consignment: Consignment) -> dict[str, Money]:
        fastline_price = self._fastline_quote(consignment.zone, consignment.weight_kg)
        airco_cents = self._airco_price(
            destination=consignment.zone, grams=int(consignment.weight_kg * 1000)
        )
        return {"AIRCO": Money(Decimal(airco_cents) / 100), "FASTLINE": Money(fastline_price)}

    def _with_margin(self, price: Money) -> Money:
        total = (price.amount * self._margin).quantize(CENT, rounding=ROUND_HALF_UP)
        return Money(total, price.currency)

    def quote(self, consignment: Consignment) -> RateQuote:
        code, cheapest = _cheapest(self._prices(consignment))
        return RateQuote(consignment.id, code, self._with_margin(cheapest))
