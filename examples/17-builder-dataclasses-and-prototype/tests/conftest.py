"""The booking table shared by three forms, and the two comparison fixtures.

`_LegacyBookingRequest` and `_BookingRequestBuilder` are test fixtures that stand for code a team
inherits or an assistant writes. They are not part of the model code in `src/`.
"""

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from typing import Self

import pytest
from builder_prototype.booking import (
    DANGEROUS_GOODS_NOTE,
    BookingRequest,
    CarrierCode,
    ServiceLevel,
)
from builder_prototype.domain import BookingError, ConsignmentId, Money, Weight

_ID = ConsignmentId("CN-1")
_WEIGHT = Weight(Decimal("120"))


@dataclass(frozen=True, slots=True, kw_only=True)
class BookingInput:
    """The twelve values of one case, whichever form builds the request."""

    consignment_id: ConsignmentId = _ID
    origin: str = "NLRTM"
    destination: str = "SGSIN"
    weight: Weight = _WEIGHT
    carrier: CarrierCode = "FASTLINE"
    service: ServiceLevel = "standard"
    insured: bool = False
    declared_value: Money | None = None
    dangerous_goods: bool = False
    reference: str | None = None
    notify_party: str | None = None
    documents: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class BookingCase:
    """One row of the table: the values, and the message of the error they must raise, if any."""

    fields: BookingInput
    error: str | None


class _LegacyBookingRequest:
    """A twelve-argument positional constructor with the same checks as the dataclass."""

    def __init__(
        self,
        consignment_id: ConsignmentId,
        origin: str,
        destination: str,
        weight: Weight,
        carrier: str,
        service: str,
        insured: bool,
        declared_value: Money | None,
        dangerous_goods: bool,
        reference: str | None,
        notify_party: str | None,
        documents: tuple[str, ...],
    ) -> None:
        if origin == destination:
            raise BookingError("origin and destination must differ")
        if insured and declared_value is None:
            raise BookingError("an insured booking needs a declared value")
        if dangerous_goods and DANGEROUS_GOODS_NOTE not in documents:
            raise BookingError(f"dangerous goods need a {DANGEROUS_GOODS_NOTE}")
        self.consignment_id = consignment_id
        self.origin = origin
        self.destination = destination
        self.weight = weight
        self.carrier = carrier
        self.service = service
        self.insured = insured
        self.declared_value = declared_value
        self.dangerous_goods = dangerous_goods
        self.reference = reference
        self.notify_party = notify_party
        self.documents = documents


class _BookingRequestBuilder:
    """A fluent GoF builder. A step left out is found when `build` runs, not before."""

    def __init__(self) -> None:
        self._consignment_id: ConsignmentId | None = None
        self._origin: str | None = None
        self._destination: str | None = None
        self._weight: Weight | None = None
        self._carrier: str = "FASTLINE"
        self._service: str = "standard"
        self._insured = False
        self._declared_value: Money | None = None
        self._dangerous_goods = False
        self._reference: str | None = None
        self._notify_party: str | None = None
        self._documents: tuple[str, ...] = ()

    def consignment(self, consignment_id: ConsignmentId) -> Self:
        self._consignment_id = consignment_id
        return self

    def origin(self, origin: str) -> Self:
        self._origin = origin
        return self

    def destination(self, destination: str) -> Self:
        self._destination = destination
        return self

    def weight(self, weight: Weight) -> Self:
        self._weight = weight
        return self

    def carrier(self, carrier: str) -> Self:
        self._carrier = carrier
        return self

    def service(self, service: str) -> Self:
        self._service = service
        return self

    def insured(self, insured: bool) -> Self:
        self._insured = insured
        return self

    def declared_value(self, declared_value: Money | None) -> Self:
        self._declared_value = declared_value
        return self

    def dangerous_goods(self, dangerous_goods: bool) -> Self:
        self._dangerous_goods = dangerous_goods
        return self

    def reference(self, reference: str | None) -> Self:
        self._reference = reference
        return self

    def notify_party(self, notify_party: str | None) -> Self:
        self._notify_party = notify_party
        return self

    def documents(self, documents: tuple[str, ...]) -> Self:
        self._documents = documents
        return self

    def build(self) -> _LegacyBookingRequest:
        if (
            self._consignment_id is None
            or self._origin is None
            or self._destination is None
            or self._weight is None
        ):
            missing = [
                name
                for name, value in (
                    ("consignment", self._consignment_id),
                    ("origin", self._origin),
                    ("destination", self._destination),
                    ("weight", self._weight),
                )
                if value is None
            ]
            raise ValueError(f"builder is missing: {', '.join(missing)}")
        return _LegacyBookingRequest(
            self._consignment_id,
            self._origin,
            self._destination,
            self._weight,
            self._carrier,
            self._service,
            self._insured,
            self._declared_value,
            self._dangerous_goods,
            self._reference,
            self._notify_party,
            self._documents,
        )


def _by_keyword(f: BookingInput) -> BookingRequest:
    return BookingRequest(
        consignment_id=f.consignment_id,
        origin=f.origin,
        destination=f.destination,
        weight=f.weight,
        carrier=f.carrier,
        service=f.service,
        insured=f.insured,
        declared_value=f.declared_value,
        dangerous_goods=f.dangerous_goods,
        reference=f.reference,
        notify_party=f.notify_party,
        documents=f.documents,
    )


def _by_position(f: BookingInput) -> _LegacyBookingRequest:
    return _LegacyBookingRequest(
        f.consignment_id,
        f.origin,
        f.destination,
        f.weight,
        f.carrier,
        f.service,
        f.insured,
        f.declared_value,
        f.dangerous_goods,
        f.reference,
        f.notify_party,
        f.documents,
    )


def _by_builder(f: BookingInput) -> _LegacyBookingRequest:
    return (
        _BookingRequestBuilder()
        .consignment(f.consignment_id)
        .origin(f.origin)
        .destination(f.destination)
        .weight(f.weight)
        .carrier(f.carrier)
        .service(f.service)
        .insured(f.insured)
        .declared_value(f.declared_value)
        .dangerous_goods(f.dangerous_goods)
        .reference(f.reference)
        .notify_party(f.notify_party)
        .documents(f.documents)
        .build()
    )


_BUILDERS: dict[str, Callable[[BookingInput], object]] = {
    "keyword": _by_keyword,
    "positional": _by_position,
    "builder": _by_builder,
}

_CASES: dict[str, BookingCase] = {
    "minimal": BookingCase(BookingInput(), None),
    "insured-without-value": BookingCase(BookingInput(insured=True), "declared value"),
    "dangerous-without-note": BookingCase(
        BookingInput(dangerous_goods=True, documents=("commercial invoice",)),
        DANGEROUS_GOODS_NOTE,
    ),
    "same-ports": BookingCase(BookingInput(origin="NLRTM", destination="NLRTM"), "must differ"),
}


@pytest.fixture(params=list(_CASES), ids=list(_CASES))
def booking_case(request: pytest.FixtureRequest) -> BookingCase:
    """The four-case booking table."""
    return _CASES[request.param]


@pytest.fixture(params=list(_BUILDERS), ids=list(_BUILDERS))
def build(request: pytest.FixtureRequest) -> Callable[[BookingInput], object]:
    """The keyword-only dataclass, the positional constructor and the fluent builder."""
    return _BUILDERS[request.param]


@pytest.fixture
def legacy_request() -> type[_LegacyBookingRequest]:
    return _LegacyBookingRequest


@pytest.fixture
def new_builder() -> type[_BookingRequestBuilder]:
    return _BookingRequestBuilder


def _view(request: object) -> dict[str, object]:
    return {f.name: getattr(request, f.name) for f in dataclasses.fields(BookingInput)}


@pytest.fixture
def view() -> Callable[[object], dict[str, object]]:
    """The twelve field values of any of the three forms, by name."""
    return _view
