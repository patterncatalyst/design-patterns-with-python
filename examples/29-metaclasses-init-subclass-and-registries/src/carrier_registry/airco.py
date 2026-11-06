"""The Airco gateway. Importing this module registers the AIRCO code."""

from carrier_registry.carriers import CarrierBase, ConsignmentId


class AircoGateway(CarrierBase, code="AIRCO"):
    def book(self, consignment_id: ConsignmentId, /) -> str:
        return f"AC-{consignment_id}"
