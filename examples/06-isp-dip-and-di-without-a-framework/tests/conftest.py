import pytest
from isp_dip_di.domain import BookingRequest, Consignment, ConsignmentId, Weight


@pytest.fixture
def consignment() -> Consignment:
    return Consignment(
        id=ConsignmentId("CN-00000001"), weight=Weight(100.0), origin="NLRTM", destination="SGSIN"
    )


@pytest.fixture
def request_for(consignment: Consignment) -> BookingRequest:
    return BookingRequest(consignment=consignment)


@pytest.fixture
def records() -> list[str]:
    return []
