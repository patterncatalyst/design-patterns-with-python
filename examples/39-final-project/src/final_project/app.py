"""The composition root: the one module that chooses the concrete carrier."""

from final_project.carriers import FastlineClient, FastlineGateway
from final_project.desk import BookingDesk
from final_project.domain import HandlingEvent
from final_project.rating import PricingRule, per_kg
from final_project.stowage import SlotPlan
from final_project.tracking import Signal, TrackingHistory


def build_desk(
    *,
    client: FastlineClient,
    plan: SlotPlan,
    history: TrackingHistory,
    rule: PricingRule = per_kg,
) -> BookingDesk:
    """Choose the carrier, the pricing rule and the subscriber, then hand the desk its parts."""
    events = Signal[HandlingEvent]()
    events.subscribe(history.record)
    return BookingDesk(rule=rule, plan=plan, gateway=FastlineGateway(client), events=events)
