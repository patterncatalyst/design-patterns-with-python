"""The rating engine after its constructor was parameterised, inherited with no tests.

The carriers are keyword parameters whose defaults are the real SDK calls, so a test passes plain
functions. Nothing else about the engine has been touched: the only tests it comes with are the
intent rows, which were written from the requirement. The module is the subject, so it is kept as
found.
"""

from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

from fowler_feathers import airco
from fowler_feathers.domain import Consignment, Money, RateQuote
from fowler_feathers.fastline import request_quote

MARGIN = Decimal("1.10")

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
