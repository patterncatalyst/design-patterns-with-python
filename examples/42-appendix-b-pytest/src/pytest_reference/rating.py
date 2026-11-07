"""Rating a consignment by weight and zone, singly and in a batch."""

import logging
import warnings
from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal

from pytest_reference.domain import Consignment

CENT = Decimal("0.01")
MAX_KILOGRAMS = Decimal("1000")

# Illustrative rates per kilogram.
RATES: frozendict[str, Decimal] = frozendict({"EU": Decimal("0.45"), "ASIA": Decimal("1.20")})

_log = logging.getLogger(__name__)


class RatingError(LookupError):
    """No rate is known for the consignment's zone."""


class OverweightError(ValueError):
    """The consignment is heavier than the maximum the rater accepts."""


def quote(consignment: Consignment, /) -> Decimal:
    """Price a consignment: weight times the zone's rate, rounded half up to the cent."""
    try:
        rate = RATES[consignment.zone]
    except KeyError:
        raise RatingError(f"no rate for zone {consignment.zone}") from None
    if consignment.weight.kilograms > MAX_KILOGRAMS:
        raise OverweightError(f"{consignment.id} is over {MAX_KILOGRAMS} kg")
    total = (consignment.weight.kilograms * rate).quantize(CENT, rounding=ROUND_HALF_UP)
    _log.info("quoted %s at %s", consignment.id, total)
    return total


def rate_batch(consignments: Iterable[Consignment], /) -> list[Decimal]:
    """Quote every consignment, or raise one group holding every failure."""
    quotes: list[Decimal] = []
    failures: list[RatingError | OverweightError] = []
    for consignment in consignments:
        try:
            quotes.append(quote(consignment))
        except (RatingError, OverweightError) as error:
            failures.append(error)
    if failures:
        raise ExceptionGroup("batch failed", failures)
    return quotes


@warnings.deprecated("use quote")
def legacy_quote(consignment: Consignment, /) -> Decimal:
    """The old name for ``quote``."""
    return quote(consignment)
