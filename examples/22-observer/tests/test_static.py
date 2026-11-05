import os
import re
from pathlib import Path

import mypy.api
import pytest

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


_SUBSCRIBER_FOR_ANOTHER_EVENT = """
from observer.domain import HandlingEvent
from observer.signal import Signal


def on_text(event: str, /) -> None: ...


signal = Signal[HandlingEvent]()
signal.subscribe(on_text)
"""

_WRONG_EVENT = """
from observer.domain import HandlingEvent
from observer.signal import Signal

signal = Signal[HandlingEvent]()
signal.publish("loaded")
"""

# Reduced model: a bus keyed by string topics, with `Any` payloads. It is not part of the example.
_TOPIC_BUS = """
from collections import defaultdict
from collections.abc import Callable
from typing import Any


class Bus:
    def __init__(self) -> None:
        self._handlers: defaultdict[str, list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable[[Any], None]) -> None:
        self._handlers[topic].append(handler)

    def publish(self, topic: str, payload: Any) -> None:
        for handler in self._handlers[topic]:
            handler(payload)


def on_loaded(event: dict[str, str]) -> None: ...


bus = Bus()
bus.subscribe("handling.loaded", on_loaded)
"""

_TOPIC_BUS_USES = {
    "typo-topic": 'bus.publish("handling.laoded", {"kind": "loaded"})\n',
    "wrong-payload": 'bus.publish("handling.loaded", 42)\n',
}

_SLOTTED_SUBSCRIBER = """
from observer.domain import HandlingEvent
from observer.signal import Signal


class Slotted:
    __slots__ = ("seen",)

    def __init__(self) -> None:
        self.seen = 0

    def record(self, event: HandlingEvent, /) -> None:
        self.seen += 1


signal = Signal[HandlingEvent]()
signal.subscribe(Slotted().record)
"""


def test_mypy_refuses_a_subscriber_for_another_event_type(tmp_path: Path) -> None:
    stdout, status = _run(_SUBSCRIBER_FOR_ANOTHER_EVENT, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'expected "Callable[[HandlingEvent], None]"' in stdout


def test_mypy_refuses_publishing_the_wrong_event(tmp_path: Path) -> None:
    stdout, status = _run(_WRONG_EVENT, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"arg-type"}
    assert 'expected "HandlingEvent"' in stdout


@pytest.mark.parametrize("use", _TOPIC_BUS_USES)
def test_mypy_accepts_a_typo_in_a_string_topic_bus(use: str, tmp_path: Path) -> None:
    stdout, status = _run(_TOPIC_BUS + _TOPIC_BUS_USES[use], tmp_path)

    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""


def test_mypy_cannot_see_a_subscriber_that_refuses_weak_references(tmp_path: Path) -> None:
    stdout, status = _run(_SLOTTED_SUBSCRIBER, tmp_path)

    assert status == 0
    assert _codes(stdout) == set()
    assert stdout == ""
