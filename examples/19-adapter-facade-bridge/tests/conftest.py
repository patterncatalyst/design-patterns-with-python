"""Fixtures. The comparison forms (class adapter, class-per-pair bookings, a branching caller)
live here as fixture parameters so that they run the same behaviour tables as the model code."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from decimal import ROUND_HALF_UP, Decimal

import pytest
from adapter_facade_bridge.bookings import InsuredBooking, StandardBooking
from adapter_facade_bridge.domain import (
    Booking,
    Consignment,
    ConsignmentId,
    Money,
    Weight,
)
from adapter_facade_bridge.gateways import CarrierGateway, FastlineGateway
from adapter_facade_bridge.sdks import AircoClient, FastlineClient

_HUNDREDTH = Decimal("0.01")
_DECLARED = Money(Decimal("250.00"), "EUR")


@pytest.fixture
def consignment() -> Consignment:
    return Consignment(
        id=ConsignmentId("CN-1"),
        weight=Weight(Decimal(10)),
        origin="NLRTM",
        destination="SGSIN",
    )


@pytest.fixture
def declared_value() -> Money:
    return _DECLARED


@pytest.fixture
def airco_client() -> AircoClient:
    return AircoClient()


@pytest.fixture
def fastline_client() -> FastlineClient:
    return FastlineClient()


@pytest.fixture
def gateways(
    airco_client: AircoClient, fastline_client: FastlineClient
) -> Mapping[str, CarrierGateway]:
    """The registry the desk uses, over recording clients that belong to the test."""
    return {"AIRCO": airco_client, "FASTLINE": FastlineGateway(fastline_client)}


@pytest.fixture(params=["FASTLINE", "AIRCO"])
def carrier(request: pytest.FixtureRequest) -> str:
    code: str = request.param
    return code


@pytest.fixture
def expected_reference(carrier: str) -> str:
    return {"FASTLINE": "FL-1001", "AIRCO": "AC-CN-1"}[carrier]


@pytest.fixture
def sent_to_sdk(
    carrier: str, airco_client: AircoClient, fastline_client: FastlineClient
) -> Sequence[object]:
    """What the carrier's SDK recorded for the booking call. The list fills as the test runs."""
    return fastline_client.payloads if carrier == "FASTLINE" else airco_client.booked


@pytest.fixture
def expected_sent_to_sdk(carrier: str) -> Sequence[object]:
    if carrier == "FASTLINE":
        return [{"ref": "CN-1", "weight_lb": "22.05"}]
    return [("CN-1", Weight(Decimal(10)))]


@pytest.fixture
def cover_sent_to_sdk(
    carrier: str, airco_client: AircoClient, fastline_client: FastlineClient
) -> Sequence[object]:
    """What the carrier's SDK recorded for the cover call."""
    return fastline_client.covers if carrier == "FASTLINE" else airco_client.insured


@pytest.fixture
def expected_cover_sent_to_sdk(carrier: str) -> Sequence[object]:
    if carrier == "FASTLINE":
        return [(1001, 25000, "EUR")]
    return [("AC-CN-1", _DECLARED)]


# Comparison: a class adapter. Inheriting from the SDK client makes the client's own methods part
# of the adapter's public surface.
class _FastlineClassAdapter(FastlineClient):
    def book(self, consignment_id: ConsignmentId, weight: Weight, /) -> str:
        payload = {
            "ref": consignment_id,
            "weight_lb": str(weight.pounds.quantize(_HUNDREDTH, rounding=ROUND_HALF_UP)),
        }
        return f"FL-{self.submit_shipment(payload).tracking_number}"

    def insure(self, reference: str, value: Money, /) -> None:
        cents = int(value.amount.scaleb(2))
        self.add_cover(int(reference.removeprefix("FL-")), cents, value.currency)


@pytest.fixture
def class_adapter() -> CarrierGateway:
    return _FastlineClassAdapter()


@pytest.fixture(params=["object-adapter", "class-adapter"])
def gateway_form(request: pytest.FixtureRequest) -> tuple[CarrierGateway, FastlineClient]:
    """A Fastline gateway and the recording client behind it, in each adapter form."""
    if request.param == "object-adapter":
        client = FastlineClient()
        return FastlineGateway(client), client
    adapter = _FastlineClassAdapter()
    return adapter, adapter


# Comparison: one class per kind and carrier. Each pair repeats the carrier's translation.
class _CarrierBooking(ABC):
    @abstractmethod
    def place(self, consignment: Consignment, carrier: str) -> Booking: ...


def _fastline_payload(consignment: Consignment) -> dict[str, str]:
    pounds = consignment.weight.pounds.quantize(_HUNDREDTH, rounding=ROUND_HALF_UP)
    return {"ref": consignment.id, "weight_lb": str(pounds)}


class _FastlineStandardBooking(_CarrierBooking):
    def __init__(self, client: FastlineClient) -> None:
        self._client = client

    def place(self, consignment: Consignment, carrier: str) -> Booking:
        receipt = self._client.submit_shipment(_fastline_payload(consignment))
        return Booking(carrier, f"FL-{receipt.tracking_number}")


class _FastlineInsuredBooking(_CarrierBooking):
    def __init__(self, client: FastlineClient, declared_value: Money) -> None:
        self._client = client
        self._declared_value = declared_value

    def place(self, consignment: Consignment, carrier: str) -> Booking:
        receipt = self._client.submit_shipment(_fastline_payload(consignment))
        cents = int(self._declared_value.amount.scaleb(2))
        self._client.add_cover(receipt.tracking_number, cents, self._declared_value.currency)
        return Booking(carrier, f"FL-{receipt.tracking_number}", self._declared_value)


class _AircoStandardBooking(_CarrierBooking):
    def __init__(self, client: AircoClient) -> None:
        self._client = client

    def place(self, consignment: Consignment, carrier: str) -> Booking:
        return Booking(carrier, self._client.book(consignment.id, consignment.weight))


class _AircoInsuredBooking(_CarrierBooking):
    def __init__(self, client: AircoClient, declared_value: Money) -> None:
        self._client = client
        self._declared_value = declared_value

    def place(self, consignment: Consignment, carrier: str) -> Booking:
        reference = self._client.book(consignment.id, consignment.weight)
        self._client.insure(reference, self._declared_value)
        return Booking(carrier, reference, self._declared_value)


@pytest.fixture(params=["bridge", "class-per-pair"])
def booking_form(request: pytest.FixtureRequest) -> str:
    form: str = request.param
    return form


@pytest.fixture(params=["standard", "insured"])
def booking_kind(request: pytest.FixtureRequest) -> str:
    kind: str = request.param
    return kind


@pytest.fixture
def place(
    booking_form: str,
    booking_kind: str,
    carrier: str,
    gateways: Mapping[str, CarrierGateway],
    airco_client: AircoClient,
    fastline_client: FastlineClient,
    declared_value: Money,
) -> Callable[[Consignment], Booking]:
    """Place a booking of the parametrised kind with the parametrised carrier, in either design."""
    insured = booking_kind == "insured"
    pair: _CarrierBooking
    if booking_form == "bridge":
        gateway = gateways[carrier]
        bridge = InsuredBooking(gateway, declared_value) if insured else StandardBooking(gateway)
        return lambda consignment: bridge.place(consignment, carrier)
    if carrier == "FASTLINE":
        pair = (
            _FastlineInsuredBooking(fastline_client, declared_value)
            if insured
            else _FastlineStandardBooking(fastline_client)
        )
    else:
        pair = (
            _AircoInsuredBooking(airco_client, declared_value)
            if insured
            else _AircoStandardBooking(airco_client)
        )
    return lambda consignment: pair.place(consignment, carrier)


# Comparison: the caller that branches on the carrier code and reaches into each SDK itself.
def _book_by_branching(
    consignment: Consignment, carrier: str, airco: AircoClient, fastline: FastlineClient
) -> Booking:
    if carrier == "FASTLINE":
        payload = {"ref": consignment.id, "weight_lb": str(consignment.weight.kilograms)}
        receipt = fastline.submit_shipment(payload)
        return Booking(carrier, f"FL-{receipt.tracking_number}")
    return Booking(carrier, airco.book(consignment.id, consignment.weight))


@pytest.fixture
def book_by_branching(
    airco_client: AircoClient, fastline_client: FastlineClient
) -> Callable[[Consignment, str], Booking]:
    def book(consignment: Consignment, carrier: str) -> Booking:
        return _book_by_branching(consignment, carrier, airco_client, fastline_client)

    return book
