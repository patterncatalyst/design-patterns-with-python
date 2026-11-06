"""The class becomes a function: the carriers are a required mapping, bound once at the root.

The engine held nothing but its carriers and a margin, so ``quote`` takes them as arguments.
``quoters`` has no default: a caller that forgets it is reported by mypy and fails at the call.
"""

from collections.abc import Mapping
from decimal import ROUND_HALF_UP, Decimal
from functools import partial

from dependency_breaking.domain import Consignment, Money, RateQuote
from dependency_breaking.fastline import request_quote
from dependency_breaking.legacy import MARGIN
from dependency_breaking.wrapped import CarrierQuoter, airco_quote

STANDARD_QUOTERS: Mapping[str, CarrierQuoter] = frozendict(
    {"AIRCO": airco_quote, "FASTLINE": request_quote}
)


def quote(
    consignment: Consignment,
    /,
    *,
    quoters: Mapping[str, CarrierQuoter],
    margin: Decimal = MARGIN,
) -> RateQuote:
    """Quote a consignment with the cheapest of the given carriers, plus a margin."""
    prices = {
        code: quoter(consignment.zone, consignment.weight_kg) for code, quoter in quoters.items()
    }
    code, cheapest = min(prices.items(), key=lambda item: (item[1], item[0]))
    total = (cheapest * margin).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return RateQuote(consignment.id, code, Money(total))


quote_standard = partial(quote, quoters=STANDARD_QUOTERS)
