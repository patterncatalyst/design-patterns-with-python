"""Parameterize Constructor: the carriers become keyword parameters with the real calls as defaults.

Existing callers construct ``RateEngine()`` as before. A test passes fakes as arguments.
"""

from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

from dependency_breaking import airco
from dependency_breaking.domain import Consignment, Money, RateQuote
from dependency_breaking.fastline import request_quote
from dependency_breaking.legacy import MARGIN

type FastlineQuote = Callable[[str, Decimal], Decimal]


class AircoPrice(Protocol):
    """The shape of ``airco.price``: keyword-only, grams in, cents out."""

    def __call__(self, *, destination: str, grams: int) -> int: ...


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

    def quote(self, consignment: Consignment) -> RateQuote:
        fastline_price = self._fastline_quote(consignment.zone, consignment.weight_kg)
        airco_cents = self._airco_price(
            destination=consignment.zone, grams=int(consignment.weight_kg * 1000)
        )
        prices = {"AIRCO": Decimal(airco_cents) / 100, "FASTLINE": fastline_price}
        code, cheapest = min(prices.items(), key=lambda item: (item[1], item[0]))
        total = (cheapest * self._margin).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return RateQuote(consignment.id, code, Money(total))
