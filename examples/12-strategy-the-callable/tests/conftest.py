from decimal import Decimal

import pytest
from strategy_callable.domain import Consignment, ConsignmentId, Weight


@pytest.fixture
def consignment() -> Consignment:
    return Consignment(
        id=ConsignmentId("CN-00000001"),
        weight=Weight(Decimal("10")),
        zone="EU",
        destination="NLRTM",
    )


@pytest.fixture
def asia_consignment() -> Consignment:
    return Consignment(
        id=ConsignmentId("CN-00000002"),
        weight=Weight(Decimal("10")),
        zone="ASIA",
        destination="SGSIN",
    )
