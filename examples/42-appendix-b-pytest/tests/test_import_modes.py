"""Import modes: what the default does to same-named test files, and what importlib forbids."""

import pytest

pytest_plugins = ["pytester"]

_ZONE_TEST = """
from pytest_reference.rating import RATES

def test_zone():
    assert "{zone}" in RATES
"""


def _two_files_with_one_basename(pytester: pytest.Pytester) -> None:
    for zone in ("EU", "ASIA"):
        tests = pytester.mkdir(zone.lower()) / "tests"
        tests.mkdir()
        (tests / "test_zones.py").write_text(_ZONE_TEST.replace("{zone}", zone))


def test_same_basename_test_files_collide_under_prepend(pytester: pytest.Pytester) -> None:
    _two_files_with_one_basename(pytester)

    result = pytester.runpytest("--import-mode=prepend", "eu", "asia")

    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*import file mismatch*"])


def test_importlib_mode_gives_each_test_file_a_unique_name(pytester: pytest.Pytester) -> None:
    _two_files_with_one_basename(pytester)

    result = pytester.runpytest("--import-mode=importlib", "eu", "asia")

    result.assert_outcomes(passed=2)


def test_importlib_mode_cannot_import_conftest_by_name(pytester: pytest.Pytester) -> None:
    tests = pytester.mkdir("tests")
    (tests / "conftest.py").write_text("LIMIT = 3\n")
    (tests / "test_limit.py").write_text(
        "from conftest import LIMIT\n\ndef test_limit():\n    assert LIMIT == 3\n"
    )

    prepend = pytester.runpytest("--import-mode=prepend", "tests")
    importlib = pytester.runpytest("--import-mode=importlib", "tests")

    prepend.assert_outcomes(passed=1)
    importlib.assert_outcomes(errors=1)
    importlib.stdout.fnmatch_lines(["*ModuleNotFoundError: No module named 'conftest'*"])


def test_pytest_plugins_in_a_non_root_conftest_fails_collection(
    pytester: pytest.Pytester,
) -> None:
    """The same line in a test module loads the plugin from the inner root."""
    sub = pytester.mkdir("sub")
    (sub / "conftest.py").write_text('pytest_plugins = ["pytester"]\n')
    (sub / "test_plain.py").write_text("def test_plain():\n    pass\n")
    pytester.makepyfile(
        test_module='pytest_plugins = ["pytester"]\n\ndef test_plain():\n    pass\n'
    )

    from_conftest = pytester.runpytest()
    from_module = pytester.runpytest("test_module.py")

    from_conftest.assert_outcomes(errors=1)
    from_conftest.stdout.fnmatch_lines(
        ["*Defining 'pytest_plugins' in a non-top-level conftest is no longer supported*"]
    )
    from_module.assert_outcomes(passed=1)
