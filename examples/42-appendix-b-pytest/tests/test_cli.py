"""Command-line options: selection, stopping, rerunning, listing and overriding."""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from conftest import NodeIds

pytest_plugins = ["pytester"]

_QUOTES = """
def test_quote_eu():
    pass

def test_quote_asia():
    pass
"""

_FAIL_THEN_PASS = """
def test_failing():
    assert False

def test_passing():
    pass
"""

_PASS_THEN_FAIL = """
def test_passing():
    pass

def test_failing():
    assert False
"""


def test_k_selects_by_name_expression(pytester: pytest.Pytester, node_ids: NodeIds) -> None:
    pytester.makepyfile(test_rates=_QUOTES)

    selected = pytester.runpytest("-k", "asia")
    listed = pytester.runpytest("-k", "asia", "--collect-only", "-q")

    selected.assert_outcomes(passed=1, deselected=1)
    assert node_ids(listed) == ["test_rates.py::test_quote_asia"]


def test_m_selects_by_marker(pytester: pytest.Pytester, node_ids: NodeIds) -> None:
    """Credits the inner ``markers`` line: without it ``--strict-markers`` refuses the mark."""
    pytester.makepyprojecttoml(
        '[tool.pytest.ini_options]\naddopts = "--strict-markers"\n'
        'markers = ["bulk: consignments over a tonne"]\n'
    )
    pytester.makepyfile(
        test_bulk="""
        import pytest

        @pytest.mark.bulk
        def test_pallet():
            pass

        def test_parcel():
            pass
        """
    )

    selected = pytester.runpytest("-m", "bulk")
    listed = pytester.runpytest("-m", "bulk", "--collect-only", "-q")
    excluded = pytester.runpytest("-m", "not bulk", "--collect-only", "-q")

    selected.assert_outcomes(passed=1, deselected=1)
    assert node_ids(listed) == ["test_bulk.py::test_pallet"]
    assert node_ids(excluded) == ["test_bulk.py::test_parcel"]


def test_x_stops_at_the_first_failure(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(test_stop=_FAIL_THEN_PASS)

    everything = pytester.runpytest()
    stopped = pytester.runpytest("-x")

    everything.assert_outcomes(failed=1, passed=1)
    stopped.assert_outcomes(failed=1)


def test_lf_reruns_only_the_last_failures(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(test_rerun=_PASS_THEN_FAIL)

    first = pytester.runpytest()
    rerun = pytester.runpytest("--lf")

    first.assert_outcomes(failed=1, passed=1)
    rerun.assert_outcomes(failed=1)
    rerun.stdout.fnmatch_lines(["run-last-failure: rerun previous 1 failure*"])


def test_collect_only_lists_without_running(pytester: pytest.Pytester, node_ids: NodeIds) -> None:
    pytester.makepyfile(
        test_listing="""
        import pathlib

        def test_leaves_a_file():
            pathlib.Path(__file__).with_name("ran.txt").write_text("ran")
        """
    )

    listed = pytester.runpytest("--collect-only", "-q")
    assert node_ids(listed) == ["test_listing.py::test_leaves_a_file"]
    assert not (pytester.path / "ran.txt").exists()

    pytester.runpytest().assert_outcomes(passed=1)
    assert (pytester.path / "ran.txt").exists()


def test_o_overrides_an_ini_option(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        test_xpass="""
        import pytest

        @pytest.mark.xfail
        def test_passes_anyway():
            pass
        """
    )
    pytester.makepyprojecttoml("[tool.pytest.ini_options]\nxfail_strict = true\n")

    configured = pytester.runpytest()
    overridden = pytester.runpytest("-o", "xfail_strict=false")

    configured.assert_outcomes(failed=1)
    overridden.assert_outcomes(xpassed=1)
