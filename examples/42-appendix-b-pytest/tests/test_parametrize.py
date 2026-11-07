"""Parametrisation: case ids, per-case marks, stacked decorators and duplicate ids."""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from conftest import NodeIds

pytest_plugins = ["pytester"]


def test_pytest_param_ids_name_the_cases(pytester: pytest.Pytester, node_ids: NodeIds) -> None:
    pytester.makepyfile(
        test_ids="""
        import pytest

        @pytest.mark.parametrize(
            ("zone", "total"),
            [
                pytest.param("EU", "4.50", id="europe"),
                pytest.param("ASIA", "12.00", id="asia"),
            ],
        )
        def test_zone(zone, total):
            pass
        """
    )

    result = pytester.runpytest("--collect-only", "-q")

    assert node_ids(result) == ["test_ids.py::test_zone[europe]", "test_ids.py::test_zone[asia]"]


def test_a_case_can_carry_its_own_mark(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        test_marks="""
        from decimal import Decimal
        import pytest
        from pytest_reference.domain import Consignment, ConsignmentId, Weight
        from pytest_reference.rating import RatingError, quote

        unknown = pytest.param(
            "MARS", marks=pytest.mark.xfail(strict=True, raises=RatingError), id="unknown"
        )

        @pytest.mark.parametrize("zone", ["EU", unknown, "ASIA"])
        def test_quote(zone):
            quote(Consignment(ConsignmentId("CN-1"), zone, Weight(Decimal("1"))))
        """
    )

    result = pytester.runpytest()

    result.assert_outcomes(passed=2, xfailed=1)


def test_stacked_parametrize_takes_the_cross_product(
    pytester: pytest.Pytester, node_ids: NodeIds
) -> None:
    pytester.makepyfile(
        test_stack="""
        import pytest

        @pytest.mark.parametrize("zone", ["EU", "ASIA"])
        @pytest.mark.parametrize("kilograms", ["1", "5", "10"])
        def test_pair(zone, kilograms):
            pass
        """
    )

    collected = pytester.runpytest("--collect-only", "-q")
    ran = pytester.runpytest()

    assert node_ids(collected) == [
        "test_stack.py::test_pair[1-EU]",
        "test_stack.py::test_pair[1-ASIA]",
        "test_stack.py::test_pair[5-EU]",
        "test_stack.py::test_pair[5-ASIA]",
        "test_stack.py::test_pair[10-EU]",
        "test_stack.py::test_pair[10-ASIA]",
    ]
    ran.assert_outcomes(passed=6)


def test_duplicate_ids_get_a_suffix_unless_strict_parametrization_ids(
    pytester: pytest.Pytester, node_ids: NodeIds
) -> None:
    pytester.makepyfile(
        test_dupes="""
        import pytest

        @pytest.mark.parametrize(
            "zone", [pytest.param("EU", id="same"), pytest.param("ASIA", id="same")]
        )
        def test_zone(zone):
            pass
        """
    )
    pytester.makepyprojecttoml("[tool.pytest.ini_options]\nstrict_parametrization_ids = false\n")
    lenient = pytester.runpytest("--collect-only", "-q")

    pytester.makepyprojecttoml("[tool.pytest.ini_options]\nstrict_parametrization_ids = true\n")
    strict = pytester.runpytest()

    assert node_ids(lenient) == [
        "test_dupes.py::test_zone[same0]",
        "test_dupes.py::test_zone[same1]",
    ]
    strict.assert_outcomes(errors=1)
    strict.stdout.fnmatch_lines(["*duplicate*"])
