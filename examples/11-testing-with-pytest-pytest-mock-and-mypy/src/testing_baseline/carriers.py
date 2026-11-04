"""What the rating engine needs from a carrier."""

from dataclasses import dataclass
from typing import Protocol

from testing_baseline.domain import Consignment, Money


class CarrierTimeoutError(Exception):
    """A carrier did not answer in time."""


@dataclass(frozen=True, slots=True)
class CarrierQuote:
    """A carrier's price for one consignment."""

    carrier: str
    amount: Money


class CarrierGateway(Protocol):
    """Quote a consignment, or book it and get the carrier's reference."""

    def quote(self, consignment: Consignment, /) -> CarrierQuote: ...

    def book(self, consignment: Consignment, /) -> str: ...
