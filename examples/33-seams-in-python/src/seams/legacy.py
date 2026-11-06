"""The rating engine as it was inherited: written before anyone tested it.

The shape is the subject of the chapter, so it is kept as found. The FASTLINE function is
imported by name, AIRCO is reached through its module, both carriers are called inside
``quote``, and the margin is captured as a default argument when the class is defined.
"""

from decimal import ROUND_HALF_UP, Decimal

from seams import airco
from seams.domain import Consignment, Money, RateQuote
from seams.fastline import request_quote

MARGIN = Decimal("1.10")


class RateEngine:
    """Quote a consignment with the cheaper of two carriers, plus a margin."""

    def __init__(self, *, margin: Decimal = MARGIN) -> None:
        self._margin = margin

    def quote(self, consignment: Consignment) -> RateQuote:
        fastline_price = request_quote(consignment.zone, consignment.weight_kg)
        airco_cents = airco.price(
            destination=consignment.zone, grams=int(consignment.weight_kg * 1000)
        )
        prices = {"AIRCO": Decimal(airco_cents) / 100, "FASTLINE": fastline_price}
        code, cheapest = min(prices.items(), key=lambda item: (item[1], item[0]))
        total = (cheapest * self._margin).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return RateQuote(consignment.id, code, Money(total))
