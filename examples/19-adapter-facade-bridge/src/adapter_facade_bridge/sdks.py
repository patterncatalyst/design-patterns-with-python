"""Stand-ins for two carrier SDKs of different shapes. Each records its calls."""

from collections.abc import Mapping
from decimal import Decimal
from typing import Final

from adapter_facade_bridge.domain import Money, Weight

# Illustrative: the largest shipment Fastline accepts, in pounds.
FASTLINE_LIMIT_LB: Final = Decimal(1000)


class AircoClient:
    """Airco's SDK already has the shape of the gateway Protocol."""

    def __init__(self) -> None:
        self.booked: list[tuple[str, Weight]] = []
        self.insured: list[tuple[str, Money]] = []

    def book(self, consignment_id: str, weight: Weight) -> str:
        self.booked.append((consignment_id, weight))
        return f"AC-{consignment_id}"

    def insure(self, reference: str, value: Money) -> None:
        self.insured.append((reference, value))


class FastlineRejectedError(Exception):
    """Fastline's own rejection."""


class FastlineReceipt:
    """What Fastline returns: a number, not a reference string."""

    def __init__(self, tracking_number: int) -> None:
        self.tracking_number = tracking_number


class FastlineClient:
    """Fastline's SDK takes a payload of strings in pounds and a cover amount in cents."""

    def __init__(self) -> None:
        self.payloads: list[dict[str, str]] = []
        self.covers: list[tuple[int, int, str]] = []
        self._next_number = 1001

    def submit_shipment(self, payload: Mapping[str, str]) -> FastlineReceipt:
        self.payloads.append(dict(payload))
        pounds = Decimal(payload["weight_lb"])
        if pounds > FASTLINE_LIMIT_LB:
            raise FastlineRejectedError(f"{pounds} lb is over the {FASTLINE_LIMIT_LB} lb limit")
        number = self._next_number
        self._next_number += 1
        return FastlineReceipt(number)

    def add_cover(self, tracking_number: int, amount_cents: int, currency: str) -> None:
        self.covers.append((tracking_number, amount_cents, currency))
