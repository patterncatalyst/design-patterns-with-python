from collections.abc import Callable
from decimal import Decimal
from functools import partial

import pytest
from template_method.declarer import NetherlandsDeclarer
from template_method.domain import Commodity, Consignment, ConsignmentId, CustomsDeclaration, Money
from template_method.hooks import EU_CLASSIFICATION, EU_SCHEDULE, NETHERLANDS, declare_customs

type Declare = Callable[[Consignment], CustomsDeclaration]
type MakeConsignment = Callable[..., Consignment]


def _make_consignment(*commodities: Commodity) -> Consignment:
    return Consignment(
        id=ConsignmentId("CN-00000013"), destination="NLRTM", commodities=commodities
    )


@pytest.fixture
def make_consignment() -> MakeConsignment:
    """Build an NLRTM consignment from the commodities given."""
    return _make_consignment


@pytest.fixture
def consignment() -> Consignment:
    return _make_consignment(
        Commodity("laptops", Money(Decimal("1200.00"), "EUR")),
        Commodity("cotton t-shirts", Money(Decimal("800.00"), "EUR")),
    )


@pytest.fixture(params=["hooks", "template"])
def declare(request: pytest.FixtureRequest) -> Declare:
    """The same Netherlands declaration, issued by the function form and by the class form."""
    if request.param == "hooks":
        return partial(declare_customs, hooks=NETHERLANDS)
    return NetherlandsDeclarer(classification=EU_CLASSIFICATION, schedule=EU_SCHEDULE).declare
