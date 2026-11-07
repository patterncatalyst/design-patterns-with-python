"""The rating module's own behaviour, which the reference tests rely on."""

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from pytest_reference.domain import Weight
from pytest_reference.rating import rate_batch

if TYPE_CHECKING:
    from conftest import MakeConsignment


def test_a_non_positive_weight_is_refused() -> None:
    with pytest.raises(ValueError, match="weight must be positive"):
        Weight(Decimal("0"))


def test_a_quote_rounds_half_up_to_the_cent(make_consignment: MakeConsignment) -> None:
    """3.3 kg at 0.45 is 1.485, which half up takes to 1.49 where half even would give 1.48."""
    batch = [make_consignment(kilograms="3.3")]

    assert rate_batch(batch) == [Decimal("1.49")]


def test_a_clean_batch_returns_its_quotes_in_order(make_consignment: MakeConsignment) -> None:
    batch = [make_consignment("CN-1", zone="ASIA", kilograms="5"), make_consignment("CN-2")]

    assert rate_batch(batch) == [Decimal("6.00"), Decimal("4.50")]
