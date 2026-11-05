import os
import re
from pathlib import Path

import mypy.api

_SRC = Path(__file__).resolve().parents[1] / "src"


def _run(snippet: str, tmp_path: Path) -> tuple[str, int]:
    """Type-check a snippet strictly, finding the package through the member's src directory."""
    config = tmp_path / "mypy.ini"
    config.write_text(f"[mypy]\nmypy_path = {_SRC}\n")
    stdout, _stderr, status = mypy.api.run(
        [
            "--strict",
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


def _codes(stdout: str) -> set[str]:
    return set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE))


_CLOSE_ON_ITERATOR = """
from collections.abc import Iterator

from iterator_protocol.domain import HandlingEvent
from iterator_protocol.reading import events_from


def run() -> None:
    reader: Iterator[HandlingEvent] = events_from([])
    reader.close()
"""

_CLOSING_ON_ITERATOR = """
from collections.abc import Iterator
from contextlib import closing

from iterator_protocol.domain import HandlingEvent
from iterator_protocol.reading import events_from


def run() -> None:
    reader: Iterator[HandlingEvent] = events_from([])
    with closing(reader):
        pass
"""

_CLOSING_ON_READER = """
from contextlib import closing
from pathlib import Path

from iterator_protocol.reading import read_events


def run(path: Path) -> None:
    with closing(read_events(path)) as reader:
        for _ in reader:
            break
"""

# Reduced model: an iterator walked twice.
_SECOND_PASS = """
from collections.abc import Iterator


def twice(xs: Iterator[int]) -> tuple[int, int]:
    return sum(xs), sum(xs)
"""

# Reduced model: a function that needs a collection, given a generator.
_GENERATOR_FOR_COLLECTION = """
from collections.abc import Collection


def count_ports(ports: Collection[str]) -> int:
    return len(ports)


def run(ports: list[str]) -> int:
    return count_ports(port for port in ports)
"""

_YIELD_FROM_VALUE = """
from collections.abc import Generator

from iterator_protocol.domain import HandlingEvent
from iterator_protocol.reading import events_from


def run() -> Generator[HandlingEvent, None, str]:
    count: str = yield from events_from([])
    return count
"""

# Reduced model: a class with only __next__, used in a for loop.
_ONLY_NEXT = """
class OnlyNext:
    def __next__(self) -> str:
        raise StopIteration


def run() -> list[str]:
    seen: list[str] = []
    for item in OnlyNext():
        seen.append(item)
    return seen
"""

# Reduced model: a cursor whose __iter__ returns itself, passed as an Iterable.
_SELF_ITERATING = """
from collections.abc import Iterable
from typing import Self


class OneShot:
    def __iter__(self) -> Self:
        return self

    def __next__(self) -> str:
        raise StopIteration


def take(items: Iterable[str]) -> list[str]:
    return list(items)


def run() -> list[str]:
    return take(OneShot())
"""


def test_mypy_refuses_close_on_an_iterator(tmp_path: Path) -> None:
    stdout, status = _run(_CLOSE_ON_ITERATOR, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"attr-defined"}
    assert 'has no attribute "close"' in stdout


def test_mypy_refuses_contextlib_closing_on_an_iterator(tmp_path: Path) -> None:
    stdout, status = _run(_CLOSING_ON_ITERATOR, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"type-var"}
    assert 'of "closing" cannot be "Iterator[HandlingEvent]"' in stdout


def test_mypy_accepts_contextlib_closing_on_a_reader(tmp_path: Path) -> None:
    stdout, status = _run(_CLOSING_ON_READER, tmp_path)

    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""


def test_mypy_cannot_see_a_second_pass_over_an_iterator(tmp_path: Path) -> None:
    stdout, status = _run(_SECOND_PASS, tmp_path)

    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""


def test_mypy_refuses_a_generator_where_a_collection_is_needed(tmp_path: Path) -> None:
    stdout, status = _run(_GENERATOR_FOR_COLLECTION, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'expected "Collection[str]"' in stdout


def test_mypy_types_the_value_of_yield_from(tmp_path: Path) -> None:
    stdout, status = _run(_YIELD_FROM_VALUE, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"assignment"}
    assert 'expression has type "int", variable has type "str"' in stdout


def test_mypy_refuses_a_class_with_only_next_in_a_for_loop(tmp_path: Path) -> None:
    stdout, status = _run(_ONLY_NEXT, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"attr-defined"}
    assert "(not iterable)" in stdout


def test_mypy_accepts_a_self_iterating_history_as_an_iterable(tmp_path: Path) -> None:
    stdout, status = _run(_SELF_ITERATING, tmp_path)

    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""
