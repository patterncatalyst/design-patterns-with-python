"""Carrier: the gateway Protocol, a stand-in vendor SDK and the adapter between them."""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Protocol

from final_project.domain import Consignment


class CarrierGateway(Protocol):
    def book(self, consignment: Consignment, /) -> str: ...

    def cancel(self, reference: str, /) -> None: ...


class FastlineClient:
    """A stand-in for the carrier's SDK: grams in, a numeric receipt out, nothing on the wire."""

    def __init__(self) -> None:
        self._next_receipt = 1001
        self._open: dict[int, int] = {}

    @property
    def open(self) -> Mapping[int, int]:
        """Receipts that have not been voided, with the grams each one holds."""
        return MappingProxyType(self._open)

    def submit(self, *, grams: int, destination: str) -> int:
        receipt = self._next_receipt
        self._next_receipt += 1
        self._open[receipt] = grams
        return receipt

    def void(self, receipt: int) -> None:
        del self._open[receipt]


class FastlineGateway:
    """Adapter: kilograms become the SDK's grams, and the SDK's receipt becomes a reference."""

    def __init__(self, client: FastlineClient) -> None:
        self._client = client

    def book(self, consignment: Consignment, /) -> str:
        receipt = self._client.submit(
            grams=int(consignment.weight.kilograms * 1000), destination=consignment.destination
        )
        return f"FL-{receipt}"

    def cancel(self, reference: str, /) -> None:
        self._client.void(int(reference.removeprefix("FL-")))
