"""CPU-bound rating: pure-Python Decimal arithmetic over the weight in 100 g steps."""

from decimal import ROUND_HALF_UP, Decimal

from gil_and_performance.domain import Consignment, Money, RateQuote

_STEP = Decimal("0.1")
_CENT = Decimal("0.01")
# Illustrative prices per 100 g step.
_PRICE_PER_STEP: frozendict[str, Decimal] = frozendict(
    {"EU": Decimal("0.0042"), "ASIA": Decimal("0.0057")}
)


def quote(consignment: Consignment, /) -> RateQuote:
    """Price a consignment. Deterministic, so every executor must give the serial answer."""
    price = _PRICE_PER_STEP[consignment.zone]
    total = Decimal(0)
    for step in range(int(consignment.weight_kg / _STEP)):
        total += price * (100 + step % 7) / 100
    return RateQuote(consignment.id, Money(total.quantize(_CENT, rounding=ROUND_HALF_UP)))
