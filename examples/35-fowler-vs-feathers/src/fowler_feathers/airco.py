"""A stand-in for the AIRCO SDK.

The real SDK opens a connection to the carrier. This one does no I/O: it raises where the
connection would time out. AIRCO takes keyword-only arguments, measures in grams and answers
in cents.
"""

from fowler_feathers.domain import CarrierTimeoutError


def price(*, destination: str, grams: int) -> int:
    """Ask AIRCO for a price in cents."""
    raise CarrierTimeoutError(f"AIRCO did not answer for {destination!r}")
