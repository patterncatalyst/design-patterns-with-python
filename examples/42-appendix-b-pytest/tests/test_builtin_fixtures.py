"""Built-in fixtures: tmp_path, capsys and caplog."""

import io
import logging
from decimal import Decimal

import pytest
from pytest_reference.domain import Consignment, ConsignmentId
from pytest_reference.rating import quote
from pytest_reference.report import write_quotes

pytest_plugins = ["pytester"]


def test_tmp_path_is_a_fresh_directory_per_test(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        test_dirs="""
        import pathlib

        SEEN = pathlib.Path(__file__).with_name("seen.txt")

        def record(tmp_path):
            assert list(tmp_path.iterdir()) == []
            (tmp_path / "marker").write_text("here")
            with SEEN.open("a") as seen:
                seen.write(str(tmp_path) + "\\n")

        def test_first(tmp_path):
            record(tmp_path)

        def test_second(tmp_path):
            record(tmp_path)
        """
    )

    result = pytester.runpytest()

    result.assert_outcomes(passed=2)
    assert len(set((pytester.path / "seen.txt").read_text().splitlines())) == 2


def test_capsys_captures_what_the_report_writes(capsys: pytest.CaptureFixture[str]) -> None:
    """Credits the call-time lookup of ``sys.stdout`` in ``write_quotes``."""
    quotes = {ConsignmentId("CN-1"): Decimal("4.50")}
    buffer = io.StringIO()

    write_quotes(quotes)
    write_quotes(quotes, out=buffer)

    assert capsys.readouterr().out == "CN-1 4.50\n"
    assert buffer.getvalue() == "CN-1 4.50\n"


def test_caplog_records_the_quote_message(
    caplog: pytest.LogCaptureFixture, consignment: Consignment
) -> None:
    with caplog.at_level(logging.INFO):
        quote(consignment)

    assert caplog.messages == ["quoted CN-1 at 4.50"]
