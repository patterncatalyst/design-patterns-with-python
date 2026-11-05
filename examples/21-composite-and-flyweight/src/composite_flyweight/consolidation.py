"""Operations where a consignment and a consolidation differ, by `match` over the closed union."""

from typing import assert_never

from composite_flyweight.domain import Consignment, ConsolidatedShipment, Shipment


def consignments(shipment: Shipment) -> tuple[Consignment, ...]:
    """Every consignment beneath a shipment, depth first, in order."""
    match shipment:
        case Consignment():
            return (shipment,)
        case ConsolidatedShipment():
            return tuple(c for part in shipment.parts for c in consignments(part))
        case _ as unreachable:
            assert_never(unreachable)


def carries_dangerous_goods(shipment: Shipment) -> bool:
    """True when any consignment beneath the shipment holds dangerous goods."""
    return any(c.commodity.dangerous_goods for c in consignments(shipment))
