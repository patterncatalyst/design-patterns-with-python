"""Booking rollback: a frozen snapshot is the memento, a context manager is the caretaker."""

import copy
import re
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from decimal import Decimal

from visitor_memento_interpreter.domain import AmendmentError, ConsignmentId, DocumentKind

_LOCODE = re.compile(r"[A-Z]{5}")


@dataclass(frozen=True, slots=True, kw_only=True)
class BookingRequest:
    consignment_id: ConsignmentId
    kilograms: Decimal
    destination: str


@dataclass(frozen=True, slots=True)
class BookingSnapshot:
    """What a rollback needs: the request and an immutable copy of the documents."""

    request: BookingRequest
    documents: frozenset[DocumentKind]


@dataclass(slots=True, eq=False)
class Booking:
    """An entity: a request, the documents attached so far, and an append-only audit trail."""

    request: BookingRequest
    documents: set[DocumentKind] = field(default_factory=set)
    audit: list[str] = field(default_factory=list)

    def attach(self, kind: DocumentKind) -> None:
        self.documents.add(kind)
        self.audit.append(f"attached {kind.value}")

    def reweigh(self, kilograms: Decimal) -> None:
        self.request = copy.replace(self.request, kilograms=kilograms)
        self.audit.append(f"reweighed to {kilograms} kg")

    def redirect(self, destination: str) -> None:
        if not _LOCODE.fullmatch(destination):
            self.audit.append(f"refused redirect to {destination!r}")
            raise AmendmentError(f"not a UN/LOCODE: {destination!r}")
        self.request = copy.replace(self.request, destination=destination)
        self.audit.append(f"redirected to {destination}")

    def snapshot(self) -> BookingSnapshot:
        return BookingSnapshot(self.request, frozenset(self.documents))

    def restore(self, snapshot: BookingSnapshot) -> None:
        self.request = snapshot.request
        self.documents = set(snapshot.documents)


@contextmanager
def rollback(booking: Booking) -> Iterator[None]:
    """Undo a failed block. The audit is not captured, so a refusal survives."""
    saved = booking.snapshot()
    try:
        yield
    except Exception:
        booking.restore(saved)
        booking.audit.append("rolled back")
        raise
