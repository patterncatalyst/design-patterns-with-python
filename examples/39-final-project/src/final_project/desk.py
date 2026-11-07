"""The booking desk: one call that runs every step and undoes the completed ones on a refusal."""

from collections.abc import Callable
from contextlib import ExitStack
from dataclasses import dataclass

from final_project.billing import Invoice, LineItem
from final_project.carriers import CarrierGateway
from final_project.clearance import CustomsDeclaration, clear, declare
from final_project.domain import BookingRequest, HandlingEvent, HandlingKind
from final_project.rating import PricingRule, RateQuote, quote
from final_project.stowage import SlotId, SlotPlan
from final_project.tracking import Signal


@dataclass(frozen=True, slots=True)
class Shipment:
    quote: RateQuote
    slot: SlotId
    carrier_reference: str
    declaration: CustomsDeclaration
    invoice: Invoice


class BookingDesk:
    """Facade over rating, stowage, the carrier, customs, billing and tracking."""

    def __init__(
        self,
        *,
        rule: PricingRule,
        plan: SlotPlan,
        gateway: CarrierGateway,
        clear: Callable[[CustomsDeclaration], CustomsDeclaration] = clear,
        events: Signal[HandlingEvent],
    ) -> None:
        self._rule = rule
        self._plan = plan
        self._gateway = gateway
        self._clear = clear
        self._events = events

    def ship(self, request: BookingRequest, /) -> Shipment:
        consignment = request.consignment
        rate = quote(consignment, rule=self._rule)
        with ExitStack() as undo:
            slot = self._plan.reserve(consignment.id)
            undo.callback(self._plan.release, slot)
            reference = self._gateway.book(consignment)
            undo.callback(self._gateway.cancel, reference)
            declaration = self._clear(declare(consignment))
            undo.pop_all()
        invoice = Invoice(
            consignment.id,
            (LineItem("freight", rate.total), LineItem("duty", declaration.duty)),
        )
        self._events.publish(
            HandlingEvent(consignment.id, HandlingKind.BOOKED, self._plan.sailing.origin)
        )
        return Shipment(rate, slot, reference, declaration, invoice)
