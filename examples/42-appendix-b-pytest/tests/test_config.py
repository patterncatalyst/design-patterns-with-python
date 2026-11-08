"""Configuration lines and what they refuse, each run in an inner session with its own config."""

import warnings
from collections.abc import Iterator
from dataclasses import dataclass

import pytest

pytest_plugins = ["pytester"]

_MARKED = """
import pytest

@pytest.mark.shipping
def test_marked():
    pass
"""

_PASSING_XFAIL = """
import pytest

@pytest.mark.xfail
def test_passes_anyway():
    pass
"""

_PLAIN = "def test_plain():\n    pass\n"

_UNKNOWN_OPTION_LINE = "unknown_option = 1\n"
_UNKNOWN_OPTION = "[tool.pytest.ini_options]\n" + _UNKNOWN_OPTION_LINE

_DUPLICATE_IDS = """
import pytest

@pytest.mark.parametrize(
    "zone", [pytest.param("EU", id="same"), pytest.param("ASIA", id="same")]
)
def test_zone(zone):
    pass
"""

_WARNING = """
from decimal import Decimal
from pytest_reference.domain import Consignment, ConsignmentId, Weight
from pytest_reference.rating import legacy_quote

def test_old_name():
    legacy_quote(Consignment(ConsignmentId("CN-1"), "EU", Weight(Decimal("1"))))
"""


@pytest.fixture(autouse=True)
def fresh_warning_filters() -> Iterator[None]:
    """An in-process inner session inherits the process-wide warning filters, so clear the
    ``error`` filter the outer run applies and let each inner configuration decide."""
    with warnings.catch_warnings():
        warnings.resetwarnings()
        yield


def test_an_unregistered_marker_fails_collection_under_strict_markers(
    pytester: pytest.Pytester,
) -> None:
    pytester.makepyfile(test_marker=_MARKED)

    pytester.makepyprojecttoml('[tool.pytest.ini_options]\naddopts = "--strict-markers"\n')
    strict = pytester.runpytest()
    pytester.makepyprojecttoml('[tool.pytest.ini_options]\naddopts = ""\n')
    lenient = pytester.runpytest()

    strict.assert_outcomes(errors=1)
    strict.stdout.fnmatch_lines(["*'shipping' not found in `markers` configuration option*"])
    lenient.assert_outcomes(passed=1, warnings=1)


@pytest.mark.parametrize("option", ["xfail_strict", "strict_xfail"])
def test_a_passing_xfail_fails_the_run_under_strict_xfail(
    pytester: pytest.Pytester, option: str
) -> None:
    """Credits the option in the inner config: ``false`` turns the failure back into an xpass."""
    pytester.makepyfile(test_xfail=_PASSING_XFAIL)

    pytester.makepyprojecttoml(f"[tool.pytest.ini_options]\n{option} = true\n")
    strict = pytester.runpytest()
    pytester.makepyprojecttoml(f"[tool.pytest.ini_options]\n{option} = false\n")
    lenient = pytester.runpytest()

    strict.assert_outcomes(failed=1)
    lenient.assert_outcomes(xpassed=1)


def test_an_unknown_option_fails_under_strict_config(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(test_plain=_PLAIN)

    pytester.makepyprojecttoml(_UNKNOWN_OPTION + 'addopts = "--strict-config"\n')
    strict = pytester.runpytest()
    pytester.makepyprojecttoml(_UNKNOWN_OPTION)
    lenient = pytester.runpytest()

    assert strict.ret == pytest.ExitCode.USAGE_ERROR
    strict.stderr.fnmatch_lines(["*Unknown config option: unknown_option*"])
    lenient.assert_outcomes(passed=1, warnings=1)


def test_filterwarnings_error_turns_a_warning_into_a_failure(pytester: pytest.Pytester) -> None:
    """Credits ``filterwarnings`` in the inner config: dropping it leaves the test passing."""
    pytester.makepyfile(test_warning=_WARNING)

    pytester.makepyprojecttoml('[tool.pytest.ini_options]\nfilterwarnings = ["error"]\n')
    strict = pytester.runpytest()
    pytester.makepyprojecttoml("[tool.pytest.ini_options]\nfilterwarnings = []\n")
    lenient = pytester.runpytest()

    strict.assert_outcomes(failed=1)
    strict.stdout.fnmatch_lines(["*DeprecationWarning: use quote*"])
    lenient.assert_outcomes(passed=1, warnings=1)


@dataclass(frozen=True, slots=True)
class StrictCase:
    """One option that ``strict = true`` enables, a test file that trips it, and the outcome."""

    option: str
    source: str
    outcomes: dict[str, int] | None


@pytest.mark.parametrize(
    "case",
    [
        pytest.param(StrictCase("strict_markers", _MARKED, {"errors": 1}), id="strict_markers"),
        pytest.param(StrictCase("strict_xfail", _PASSING_XFAIL, {"failed": 1}), id="strict_xfail"),
        pytest.param(
            StrictCase("strict_parametrization_ids", _DUPLICATE_IDS, {"errors": 1}),
            id="strict_parametrization_ids",
        ),
        pytest.param(StrictCase("strict_config", _PLAIN, None), id="strict_config"),
    ],
)
def test_strict_enables_the_four_strictness_options(
    pytester: pytest.Pytester, case: StrictCase
) -> None:
    """The inner config sets ``strict = true`` and no individual option."""
    pytester.makepyfile(test_strict=case.source)
    config = "[tool.pytest.ini_options]\nstrict = true\n"
    pytester.makepyprojecttoml(config + (_UNKNOWN_OPTION_LINE if case.outcomes is None else ""))

    result = pytester.runpytest()

    if case.outcomes is None:
        assert result.ret == pytest.ExitCode.USAGE_ERROR
        result.stderr.fnmatch_lines(["*Unknown config option: unknown_option*"])
    else:
        result.assert_outcomes(**case.outcomes)


def test_the_first_config_file_wins_and_is_not_merged(pytester: pytest.Pytester) -> None:
    pytester.makepyprojecttoml('[tool.pytest.ini_options]\naddopts = "--strict-markers"\n')
    pytester.makepyfile(test_root=_MARKED)
    sub = pytester.mkdir("sub")
    (sub / "pyproject.toml").write_text('[tool.pytest.ini_options]\nminversion = "9.0"\n')
    (sub / "test_sub.py").write_text(_MARKED)

    from_root = pytester.runpytest("test_root.py")
    from_sub = pytester.runpytest("sub")

    from_root.assert_outcomes(errors=1)
    from_sub.assert_outcomes(passed=1, warnings=1)


def test_a_member_table_replaces_the_root_filter_and_names_its_own_file(
    pytester: pytest.Pytester,
) -> None:
    """The layout of a workspace member: the root table fails on warnings, the member's own
    table with ``addopts = ""`` is the one that is read when the run starts in the member."""
    pytester.makepyprojecttoml('[tool.pytest.ini_options]\nfilterwarnings = ["error"]\n')
    member = pytester.mkdir("member")
    (member / "pyproject.toml").write_text('[tool.pytest.ini_options]\naddopts = ""\n')
    (member / "test_member.py").write_text(_WARNING)

    from_root = pytester.runpytest("-c", "pyproject.toml", "member")
    from_member = pytester.runpytest("member")

    from_root.assert_outcomes(failed=1)
    from_member.assert_outcomes(passed=1, warnings=1)
    from_member.stdout.fnmatch_lines(["rootdir: *member", "configfile: pyproject.toml"])
