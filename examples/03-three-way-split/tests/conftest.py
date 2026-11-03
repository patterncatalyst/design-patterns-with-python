import pytest
from three_way_split.domain import Consignment, ConsignmentId, Weight


@pytest.fixture
def consignment() -> Consignment:
    return Consignment(
        id=ConsignmentId("CN-00012345"),
        weight=Weight(120.0),
        zone="ASIA",
        destination="SGSIN",
    )
