"""Booking policy. It owns the small contract it needs and imports only the domain types."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from isp_dip_di.domain import BookingRequest

type AuditSink = Callable[[str], None]


class BookingGateway(Protocol):
    """What booking needs from a carrier: accept a request, withdraw a reference."""

    def book(self, request: BookingRequest, /) -> str: ...

    def cancel(self, reference: str, /) -> None: ...


@dataclass(frozen=True, slots=True)
class BookingService:
    """Books and cancels through whichever gateway it is given, and audits each outcome."""

    gateway: BookingGateway
    audit: AuditSink

    def book(self, request: BookingRequest) -> str:
        reference = self.gateway.book(request)
        self.audit(f"booked {reference}")
        return reference

    def cancel(self, reference: str) -> None:
        self.gateway.cancel(reference)
        self.audit(f"cancelled {reference}")
