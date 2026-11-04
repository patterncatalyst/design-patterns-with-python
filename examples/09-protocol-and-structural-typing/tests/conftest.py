import pytest
from structural_typing.domain import Consignment, ConsignmentId, HazmatConsignment, Weight


@pytest.fixture
def consignment() -> Consignment:
    return Consignment(id=ConsignmentId("CN-00000001"), weight=Weight(100.0), destination="SGSIN")


@pytest.fixture
def hazmat() -> HazmatConsignment:
    return HazmatConsignment(
        id=ConsignmentId("CN-00000002"),
        weight=Weight(50.0),
        destination="NLRTM",
        un_number="UN1203",
    )
