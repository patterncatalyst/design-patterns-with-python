"""Booking with the cheapest carrier."""

from collections.abc import Callable, Mapping
from decimal import Decimal

from mocking_reference.carriers import CarrierGateway, CarrierTimeoutError, ConsignmentId

type Notify = Callable[[str], None]


def book_cheapest(
    gateways: Mapping[str, CarrierGateway],
    consignment_id: ConsignmentId,
    weight_kg: Decimal,
    /,
    *,
    notify: Notify,
) -> str:
    """Ask each carrier in code order, skip those that time out, and book the cheapest.

    Ties on the total go to the carrier name that sorts first. Raises ``LookupError`` when every
    carrier timed out.
    """
    offers: list[tuple[Decimal, str, str]] = []
    for code in sorted(gateways):
        try:
            quote = gateways[code].quote(consignment_id, weight_kg)
        except CarrierTimeoutError:
            continue
        offers.append((quote.total, quote.carrier, code))
    if not offers:
        raise LookupError(f"no carrier answered for {consignment_id}")
    _total, _carrier, code = min(offers)
    reference = gateways[code].book(consignment_id)
    notify(reference)
    return reference
