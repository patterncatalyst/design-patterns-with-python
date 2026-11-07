"""A stand-in for the FASTLINE SDK.

The real SDK opens a connection to the carrier. This one does no I/O: it raises where the
connection would time out, so a test that reaches it fails the way a test against a carrier
that does not answer would fail.
"""

from decimal import Decimal

from fowler_feathers.domain import CarrierTimeoutError


def request_quote(zone: str, weight_kg: Decimal) -> Decimal:
    """Ask FASTLINE for a price in euros."""
    raise CarrierTimeoutError(f"FASTLINE did not answer for {zone!r}")
