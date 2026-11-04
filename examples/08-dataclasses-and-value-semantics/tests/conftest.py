import pytest
from value_semantics.booking import BookingRequest, Consignment
from value_semantics.values import ConsignmentId, SlotId, Weight


@pytest.fixture
def consignment() -> Consignment:
    return Consignment(id=ConsignmentId("CN-00000001"), weight=Weight(100.0), destination="SGSIN")


@pytest.fixture
def request_for(consignment: Consignment) -> BookingRequest:
    return BookingRequest(consignment=consignment)


@pytest.fixture
def slots() -> tuple[SlotId, SlotId, SlotId]:
    return SlotId(1, 0, 1), SlotId(1, 2, 1), SlotId(3, 0, 2)
