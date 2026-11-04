"""The composition root: the only module that names a concrete carrier adapter."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from functools import partial
from types import MappingProxyType
from typing import Protocol

from isp_dip_di.booking import AuditSink, BookingGateway, BookingService
from isp_dip_di.carriers import AircoGateway, FastlineGateway
from isp_dip_di.domain import ConsignmentId, TrackingHistory
from isp_dip_di.tracking import TrackingGateway, tracking_history


class CarrierGateway(BookingGateway, TrackingGateway, Protocol):
    """A whole carrier: everything booking and tracking each need, named once for the wiring."""


GATEWAYS: Mapping[str, Callable[[], CarrierGateway]] = MappingProxyType(
    {"FASTLINE": FastlineGateway, "AIRCO": AircoGateway}
)


@dataclass(frozen=True, slots=True)
class App:
    """The wired consumers: a booking service and a tracking function."""

    booking: BookingService
    track: Callable[[ConsignmentId], TrackingHistory]


def build_app(
    carrier: str,
    *,
    audit: AuditSink,
    gateways: Mapping[str, Callable[[], CarrierGateway]] = GATEWAYS,
) -> App:
    """Build one gateway for the named carrier and hand it to each consumer."""
    try:
        factory = gateways[carrier]
    except KeyError:
        known = sorted(gateways)
        raise ValueError(f"unknown carrier {carrier!r}, expected one of {known}") from None
    gateway = factory()
    return App(BookingService(gateway, audit), partial(tracking_history, gateway=gateway))
