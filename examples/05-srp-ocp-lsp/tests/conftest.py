import pytest
from srp_ocp_lsp.domain import Consignment, ConsignmentId, RateQuote, Weight


@pytest.fixture
def eu_consignment() -> Consignment:
    return Consignment(
        id=ConsignmentId("CN-00000001"), weight=Weight(100.0), zone="EU", destination="NLRTM"
    )


@pytest.fixture
def asia_consignment() -> Consignment:
    return Consignment(
        id=ConsignmentId("CN-00000002"), weight=Weight(120.0), zone="ASIA", destination="SGSIN"
    )


@pytest.fixture
def records() -> list[RateQuote]:
    return []
