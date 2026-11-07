"""Exception, exception group and warning assertions."""

from decimal import Decimal

import pytest
from pytest_reference.domain import Consignment, ConsignmentId, Weight
from pytest_reference.rating import (
    OverweightError,
    RatingError,
    legacy_quote,
    quote,
    rate_batch,
)


def _consignment(consignment_id: str, zone: str, kilograms: str) -> Consignment:
    return Consignment(ConsignmentId(consignment_id), zone, Weight(Decimal(kilograms)))


def test_raises_match_is_a_regex_search() -> None:
    """``match`` finds its pattern anywhere in the message, and an anchor can stop it matching."""
    unknown = _consignment("CN-1", "MARS", "1")

    with pytest.raises(RatingError, match="zone MARS"):
        quote(unknown)

    with (
        pytest.raises(AssertionError, match="Regex pattern did not match"),
        pytest.raises(RatingError, match=r"^zone MARS"),
    ):
        quote(unknown)


def test_raises_check_tests_the_exception_object() -> None:
    heavy = _consignment("CN-1", "EU", "1001")

    with pytest.raises(OverweightError, check=lambda error: str(error).startswith("CN-1")):
        quote(heavy)

    with (
        pytest.raises(AssertionError, match="did not return True"),
        pytest.raises(OverweightError, check=lambda error: str(error).startswith("CN-2")),
    ):
        quote(heavy)


def test_raises_group_matches_the_batch_failures() -> None:
    batch = [
        _consignment("CN-1", "MARS", "1"),
        _consignment("CN-2", "EU", "10"),
        _consignment("CN-3", "EU", "1001"),
    ]

    with pytest.RaisesGroup(
        pytest.RaisesExc(RatingError, match="^no rate for zone MARS$"), OverweightError
    ):
        rate_batch(batch)


def test_warns_matches_the_deprecation(consignment: Consignment) -> None:
    with pytest.warns(DeprecationWarning, match="use quote"):
        total = legacy_quote(consignment)

    assert total == Decimal("4.50")
