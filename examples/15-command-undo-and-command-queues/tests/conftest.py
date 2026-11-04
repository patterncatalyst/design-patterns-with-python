from decimal import Decimal

import pytest
from command_undo.amendments import Amendment, Redirect, Reweigh, SetInstructions
from command_undo.booking import Booking
from command_undo.domain import BookingRequest, Consignment, ConsignmentId, Weight


def kg(amount: int) -> Weight:
    return Weight(Decimal(amount))


@pytest.fixture
def booking_request() -> BookingRequest:
    """A 120 kg consignment bound for Singapore, with no instructions."""
    return BookingRequest(
        consignment=Consignment(
            id=ConsignmentId("CN-00000015"), weight=kg(120), destination="SGSIN"
        )
    )


@pytest.fixture
def booking(booking_request: BookingRequest) -> Booking:
    return Booking(booking_request)


@pytest.fixture(
    params=[
        Reweigh(kg(130)),
        Redirect("MYPKG"),
        SetInstructions(frozendict({"handling": "keep dry"})),
    ],
    ids=["reweigh", "redirect", "instructions"],
)
def amendment(request: pytest.FixtureRequest) -> Amendment:
    """One amendment of each kind, each of which changes the sample request."""
    amendment: Amendment = request.param
    return amendment
