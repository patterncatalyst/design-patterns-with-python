"""The narrow gateway Protocol and the adapter that gives Fastline's SDK that shape."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol

from adapter_facade_bridge.domain import CarrierError, ConsignmentId, Money, Weight
from adapter_facade_bridge.sdks import FastlineClient, FastlineRejectedError

_HUNDREDTH = Decimal("0.01")
_FASTLINE_PREFIX = "FL-"


class CarrierGateway(Protocol):
    """The two primitives that every booking kind is built from."""

    def book(self, consignment_id: ConsignmentId, weight: Weight, /) -> str: ...

    def insure(self, reference: str, value: Money, /) -> None: ...


@dataclass(frozen=True, slots=True)
class FastlineGateway:
    """An object adapter: translates shape, units and errors behind the two Protocol methods."""

    client: FastlineClient

    def book(self, consignment_id: ConsignmentId, weight: Weight, /) -> str:
        payload = {
            "ref": consignment_id,
            "weight_lb": str(weight.pounds.quantize(_HUNDREDTH, rounding=ROUND_HALF_UP)),
        }
        try:
            receipt = self.client.submit_shipment(payload)
        except FastlineRejectedError as error:
            raise CarrierError(f"FASTLINE rejected {consignment_id}: {error}") from error
        return f"{_FASTLINE_PREFIX}{receipt.tracking_number}"

    def insure(self, reference: str, value: Money, /) -> None:
        cents = int(value.amount.scaleb(2))
        number = int(reference.removeprefix(_FASTLINE_PREFIX))
        self.client.add_cover(number, cents, value.currency)
