"""What mypy reports about a coroutine that was not awaited, and what it cannot see."""

import os
import re
from decimal import Decimal
from pathlib import Path

import mypy.api
import pytest
from asyncio_patterns.domain import Consignment, ConsignmentId
from asyncio_patterns.quoting import FastlineSource

_SRC = Path(__file__).resolve().parents[1] / "src"


def _run(snippet: str, tmp_path: Path) -> tuple[str, int]:
    """Type-check a snippet strictly, finding the package through the member's src directory."""
    config = tmp_path / "mypy.ini"
    config.write_text(f"[mypy]\nmypy_path = {_SRC}\n")
    stdout, _stderr, status = mypy.api.run(
        [
            "--strict",
            "--warn-unreachable",
            "--config-file",
            str(config),
            "--cache-dir",
            os.devnull,
            "--no-error-summary",
            "-c",
            snippet,
        ]
    )
    return stdout, status


def _codes(stdout: str) -> list[str]:
    return sorted(set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE)))


_PRELUDE = """
from asyncio_patterns.domain import Consignment, RateQuote
from asyncio_patterns.quoting import RateSource, cheapest
"""

# A quote returned from a function declared to return one, with the await left out.
_RETURNED = (
    _PRELUDE
    + """
async def quote_for(source: RateSource, consignment: Consignment) -> RateQuote:
    return source.quote(consignment)
"""
)
_RETURNED_AWAITED = _RETURNED.replace("return source", "return await source")

# A quote requested and dropped on the floor.
_DROPPED = (
    _PRELUDE
    + """
async def ask(source: RateSource, consignment: Consignment) -> None:
    source.quote(consignment)
"""
)
_DROPPED_AWAITED = _DROPPED.replace("    source.quote", "    await source.quote")

# A source whose quote blocks, passed where a RateSource is expected, and one that is async.
_BLOCKING = (
    _PRELUDE
    + """
class BlockingSource:
    def quote(self, consignment: Consignment, /) -> RateQuote:
        raise NotImplementedError


async def best(consignment: Consignment) -> RateQuote:
    return await cheapest(consignment, [BlockingSource()])
"""
)
_ASYNC = _BLOCKING.replace("    def quote", "    async def quote")

# A coroutine bound to the throwaway name: strict mode has nothing to say about it.
_UNDERSCORE = (
    _PRELUDE
    + """
async def ask(source: RateSource, consignment: Consignment) -> None:
    _ = source.quote(consignment)
"""
)


def test_mypy_reports_a_quote_returned_without_await(tmp_path: Path) -> None:
    """Credits ``async def`` on ``RateSource.quote``: adding the await empties the list."""
    bare, bare_status = _run(_RETURNED, tmp_path)
    awaited, awaited_status = _run(_RETURNED_AWAITED, tmp_path)

    assert [_codes(bare), _codes(awaited)] == [["return-value"], []]
    assert (bare_status, awaited_status) == (1, 0)
    assert 'Maybe you forgot to use "await"?' in bare


def test_mypy_reports_a_quote_call_whose_result_is_never_used(tmp_path: Path) -> None:
    """Credits ``async def`` on ``RateSource.quote``: awaiting the call empties the list."""
    bare, bare_status = _run(_DROPPED, tmp_path)
    awaited, awaited_status = _run(_DROPPED_AWAITED, tmp_path)

    assert [_codes(bare), _codes(awaited)] == [["unused-coroutine"], []]
    assert (bare_status, awaited_status) == (1, 0)
    assert "Are you missing an await?" in bare


def test_mypy_refuses_a_blocking_source_where_a_rate_source_is_expected(tmp_path: Path) -> None:
    """Credits ``async def`` on ``RateSource.quote``: declaring it ``def quote(...) -> RateQuote |
    Awaitable[RateQuote]`` empties the first list."""
    blocking, blocking_status = _run(_BLOCKING, tmp_path)
    asynchronous, asynchronous_status = _run(_ASYNC, tmp_path)

    assert [_codes(blocking), _codes(asynchronous)] == [["list-item"], []]
    assert (blocking_status, asynchronous_status) == (1, 0)
    assert "Coroutine[Any, Any, RateQuote]" in blocking


def test_mypy_accepts_a_coroutine_bound_to_underscore(tmp_path: Path) -> None:
    """Both halves: mypy exits 0, and the runtime warns that the coroutine was never awaited."""
    stdout, status = _run(_UNDERSCORE, tmp_path)

    assert (_codes(stdout), status) == ([], 0)

    consignment = Consignment(ConsignmentId("CN-1"), "EU", Decimal("20"))

    def discard() -> None:
        _ = FastlineSource().quote(consignment)

    with pytest.warns(RuntimeWarning, match="was never awaited"):
        discard()
