"""Fixture forms: yield, scope, factory, autouse, usefixtures, indirect and getfixturevalue."""

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from pytest_reference.domain import Consignment, ConsignmentId, Weight
from pytest_reference.rating import quote

if TYPE_CHECKING:
    from conftest import MakeConsignment

pytest_plugins = ["pytester"]


def test_yield_fixtures_tear_down_in_reverse_order_of_setup(pytester: pytest.Pytester) -> None:
    """A module-scoped fixture outlives the function-scoped one that depends on it."""
    pytester.makepyfile(
        test_order="""
        import pathlib
        import pytest

        LOG = pathlib.Path(__file__).with_name("order.txt")

        def note(line):
            with LOG.open("a") as log:
                log.write(line + "\\n")

        @pytest.fixture(scope="module")
        def outer():
            note("setup outer")
            yield
            note("teardown outer")

        @pytest.fixture
        def inner(outer):
            note("setup inner")
            yield
            note("teardown inner")

        def test_first(inner):
            note("first")

        def test_second(inner):
            note("second")
        """
    )

    result = pytester.runpytest()

    result.assert_outcomes(passed=2)
    assert (pytester.path / "order.txt").read_text().splitlines() == [
        "setup outer",
        "setup inner",
        "first",
        "teardown inner",
        "setup inner",
        "second",
        "teardown inner",
        "teardown outer",
    ]


def test_a_module_scoped_fixture_is_set_up_once_for_the_module(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        test_scope="""
        import pathlib
        import pytest

        LOG = pathlib.Path(__file__).with_name("setups.txt")

        def note(line):
            with LOG.open("a") as log:
                log.write(line + "\\n")

        @pytest.fixture(scope="module")
        def shared():
            note("setup shared")

        @pytest.fixture
        def fresh():
            note("setup fresh")

        def test_first(shared, fresh):
            pass

        def test_second(shared, fresh):
            pass
        """
    )

    result = pytester.runpytest()

    result.assert_outcomes(passed=2)
    assert (pytester.path / "setups.txt").read_text().splitlines() == [
        "setup shared",
        "setup fresh",
        "setup fresh",
    ]


def test_a_factory_fixture_builds_a_fresh_object_per_call(
    make_consignment: MakeConsignment,
) -> None:
    first = make_consignment()
    second = make_consignment()
    heavier = make_consignment("CN-2", zone="ASIA", kilograms="5")

    assert first == second
    assert first is not second
    assert (heavier.id, heavier.zone, heavier.weight) == ("CN-2", "ASIA", Weight(Decimal("5")))


def test_an_autouse_fixture_runs_without_being_named(ran: list[str]) -> None:
    """Credits ``autouse=True`` on ``note_autouse``: without it ``ran`` is empty."""
    assert ran == ["autouse"]


@pytest.mark.usefixtures("note_usefixtures")
def test_usefixtures_applies_a_fixture_whose_value_is_unused(ran: list[str]) -> None:
    """Credits the mark: without it ``ran`` holds the autouse entry alone."""
    assert ran == ["autouse", "usefixtures"]


@pytest.mark.parametrize(
    ("rated", "expected"),
    [("EU", Decimal("4.50")), ("ASIA", Decimal("12.00"))],
    indirect=["rated"],
)
def test_an_indirect_parameter_reaches_the_fixture_as_request_param(
    rated: Consignment, expected: Decimal
) -> None:
    """Credits ``indirect``: without it ``rated`` is the zone name, not a ``Consignment``."""
    assert quote(rated) == expected


def test_getfixturevalue_resolves_a_fixture_by_name(request: pytest.FixtureRequest) -> None:
    resolved = request.getfixturevalue("consignment")

    assert resolved == Consignment(ConsignmentId("CN-1"), "EU", Weight(Decimal("10")))
