"""The Facade: one function over gateways and booking kinds, naming only domain types."""

from collections.abc import Mapping

from adapter_facade_bridge.bookings import InsuredBooking, StandardBooking
from adapter_facade_bridge.domain import Booking, Consignment, Money, UnknownCarrierError
from adapter_facade_bridge.gateways import CarrierGateway, FastlineGateway
from adapter_facade_bridge.sdks import AircoClient, FastlineClient

__all__ = ["default_gateways", "ship"]


def default_gateways() -> Mapping[str, CarrierGateway]:
    return frozendict({"AIRCO": AircoClient(), "FASTLINE": FastlineGateway(FastlineClient())})


def ship(
    consignment: Consignment,
    carrier: str,
    *,
    gateways: Mapping[str, CarrierGateway],
    declared_value: Money | None = None,
) -> Booking:
    try:
        gateway = gateways[carrier]
    except KeyError:
        raise UnknownCarrierError(f"unknown carrier {carrier!r}") from None
    kind: StandardBooking | InsuredBooking
    if declared_value is None:
        kind = StandardBooking(gateway)
    else:
        kind = InsuredBooking(gateway, declared_value)
    return kind.place(consignment, carrier)
