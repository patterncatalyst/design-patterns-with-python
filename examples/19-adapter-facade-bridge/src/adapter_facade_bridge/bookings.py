"""The Bridge: booking kinds on one side, carrier gateways on the other."""

from dataclasses import dataclass

from adapter_facade_bridge.domain import Booking, BookingError, Consignment, Money
from adapter_facade_bridge.gateways import CarrierGateway


@dataclass(frozen=True, slots=True)
class StandardBooking:
    """Books the consignment and nothing else."""

    gateway: CarrierGateway

    def place(self, consignment: Consignment, carrier: str) -> Booking:
        reference = self.gateway.book(consignment.id, consignment.weight)
        return Booking(carrier, reference)


@dataclass(frozen=True, slots=True)
class InsuredBooking:
    """Books the consignment, then insures it for the declared value."""

    gateway: CarrierGateway
    declared_value: Money

    def __post_init__(self) -> None:
        if self.declared_value.amount <= 0:
            raise BookingError(f"declared value must be positive, got {self.declared_value.amount}")

    def place(self, consignment: Consignment, carrier: str) -> Booking:
        reference = self.gateway.book(consignment.id, consignment.weight)
        self.gateway.insure(reference, self.declared_value)
        return Booking(carrier, reference, self.declared_value)
