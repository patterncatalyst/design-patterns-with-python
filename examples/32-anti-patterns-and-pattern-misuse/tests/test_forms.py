from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from pattern_misuse.rating import Consignment, ConsignmentId, Money, RateQuote, RatingError

if TYPE_CHECKING:
    from conftest import RatingForm

# (zone, expected total)
QUOTE_ROWS = [
    pytest.param("EU", Decimal("35.70"), id="eu"),
    pytest.param("ASIA", Decimal("78.05"), id="asia"),
]


@pytest.mark.parametrize(("zone", "total"), QUOTE_ROWS)
def test_every_rating_form_quotes_the_same_table(
    rating_form: RatingForm, zone: str, total: Decimal
) -> None:
    quoted = rating_form(Consignment(ConsignmentId("CN-1"), zone))
    assert quoted == RateQuote(ConsignmentId("CN-1"), Money(total, "EUR"))
    assert str(quoted.total.amount) == str(total)


def test_every_rating_form_refuses_an_unknown_zone(rating_form: RatingForm) -> None:
    with pytest.raises(RatingError, match="no flat fee for zone 'POLAR'") as info:
        rating_form(Consignment(ConsignmentId("CN-1"), "POLAR"))
    assert info.value.__suppress_context__ is True
