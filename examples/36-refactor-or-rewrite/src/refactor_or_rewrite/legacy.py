"""The rating engine as inherited: weight bands in an if-chain with inclusive upper limits.

Two things are kept as found. Every zone other than ASIA is priced with the EU prices, so an
unknown zone gets a quote. Each band includes its upper limit, so 5 kg is in the first band. The
module is the subject of the rewrite, not a comparison form.
"""

from decimal import ROUND_HALF_UP, Decimal

from refactor_or_rewrite.domain import MARGIN, Consignment, Money, RateQuote, RatingError

__all__ = ["MARGIN", "RateEngine"]


class RateEngine:
    """Quote a consignment by weight band, plus a margin."""

    def quote(self, consignment: Consignment) -> RateQuote:
        kg = consignment.weight.kilograms
        if consignment.zone == "ASIA":
            if kg <= 5:
                price = Decimal("30.00")
            elif kg <= 20:
                price = Decimal("55.00")
            elif kg <= 50:
                price = Decimal("98.00")
            else:
                raise RatingError(f"no band for {kg} kg")
        else:
            if kg <= 5:
                price = Decimal("12.00")
            elif kg <= 20:
                price = Decimal("25.00")
            elif kg <= 50:
                price = Decimal("48.00")
            else:
                raise RatingError(f"no band for {kg} kg")
        total = (price * MARGIN).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return RateQuote(consignment.id, Money(total))
