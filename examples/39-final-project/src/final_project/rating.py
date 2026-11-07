"""Rating: a pricing rule is a callable, chosen once and handed to ``quote``."""

from collections.abc import Callable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from final_project.domain import Consignment, ConsignmentId, Money

type PricingRule = Callable[[Consignment], Money]

CENT = Decimal("0.01")
ZONE_RATES = frozendict({"EU": Decimal("0.45"), "ASIA": Decimal("1.20")})


class RatingError(LookupError):
    """No rate is known for the consignment's zone."""


@dataclass(frozen=True, slots=True)
class RateQuote:
    consignment_id: ConsignmentId
    total: Money


def per_kg(consignment: Consignment, /) -> Money:
    """Weight times the zone's rate per kilogram, rounded half up to the cent."""
    try:
        rate = ZONE_RATES[consignment.zone]
    except KeyError:
        raise RatingError(f"no rate for zone {consignment.zone}") from None
    return Money((consignment.weight.kilograms * rate).quantize(CENT, rounding=ROUND_HALF_UP))


def quote(consignment: Consignment, /, *, rule: PricingRule) -> RateQuote:
    return RateQuote(consignment.id, rule(consignment))
