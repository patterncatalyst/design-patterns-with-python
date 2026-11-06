from collections.abc import Callable
from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING

import pytest
from pattern_misuse.rating import (
    STANDARD_TARIFF,
    Consignment,
    ConsignmentId,
    RateQuote,
    quote,
)

if TYPE_CHECKING:
    from conftest import _AccessorConsignment, _LocatedRateEngine, _ServiceLocator

CONSIGNMENT = Consignment(ConsignmentId("CN-1"), "EU")


def test_an_accessor_consignment_has_no_value_equality(
    accessor_consignment: _AccessorConsignment,
) -> None:
    twin = type(accessor_consignment)(ConsignmentId("CN-1"), "EU")
    frozen_twin = Consignment(ConsignmentId("CN-1"), "EU")
    assert (accessor_consignment == twin, frozen_twin == CONSIGNMENT) == (False, True)


def test_a_setter_lets_a_quoted_consignment_change_its_quote(
    accessor_consignment: _AccessorConsignment,
    quote_accessor: Callable[[_AccessorConsignment], RateQuote],
) -> None:
    before = quote_accessor(accessor_consignment)
    accessor_consignment.set_zone("ASIA")
    after = quote_accessor(accessor_consignment)
    assert [str(before.total.amount), str(after.total.amount)] == ["35.70", "78.05"]


def test_a_frozen_consignment_refuses_assignment() -> None:
    with pytest.raises(FrozenInstanceError, match="cannot assign to field 'zone'"):
        CONSIGNMENT.zone = "ASIA"  # type: ignore[misc]


def test_a_located_engine_fails_at_the_first_quote_when_nothing_is_registered(
    located_engine: _LocatedRateEngine,
) -> None:
    with pytest.raises(KeyError, match="tariff"):
        located_engine.quote(CONSIGNMENT)


def test_a_located_engine_quotes_once_its_tariff_is_registered(
    located_engine: _LocatedRateEngine, locator: _ServiceLocator
) -> None:
    locator.register("tariff", STANDARD_TARIFF)
    assert located_engine.quote(CONSIGNMENT) == quote(CONSIGNMENT, STANDARD_TARIFF)
