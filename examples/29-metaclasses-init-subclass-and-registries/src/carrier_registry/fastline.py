"""The Fastline gateway. Importing this module registers the FASTLINE code."""

from carrier_registry.carriers import CarrierBase, ConsignmentId


class FastlineGateway(CarrierBase, code="FASTLINE"):
    def book(self, consignment_id: ConsignmentId, /) -> str:
        return f"FL-{consignment_id}"
