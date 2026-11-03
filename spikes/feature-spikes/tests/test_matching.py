"""PDP-014 evidence: structural pattern matching over tracking events."""

import os
import textwrap
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import feature_spikes.matching as matching_module
import pytest
from feature_spikes.matching import (
    Booked,
    Delivered,
    DeliveryFailed,
    InTransit,
    PickedUp,
    TrackingEvent,
    describe,
    from_webhook,
    is_terminal,
    summarize,
)
from mypy import api as mypy_api


def test_dataclasses_generate_positional_match_args() -> None:
    assert InTransit.__match_args__ == ("location",)
    assert Delivered.__match_args__ == ("signed_by",)


@pytest.mark.parametrize(
    ("event", "expected"),
    [
        (Booked("BK-1"), "booked as BK-1"),
        (PickedUp("Ines"), "picked up by Ines"),
        (InTransit("customs"), "held at a border crossing"),
        (InTransit("border"), "held at a border crossing"),
        (InTransit("depot-7"), "sorting at depot-7"),
        (InTransit("Rotterdam"), "in transit at Rotterdam"),
        (Delivered("A. Okafor"), "delivered, signed by A. Okafor"),
        (DeliveryFailed("no access"), "delivery failed: no access"),
    ],
)
def test_describe_uses_class_patterns_guards_and_or_patterns(
    event: TrackingEvent, expected: str
) -> None:
    assert describe(event) == expected


def test_is_terminal_groups_classes_with_or_patterns() -> None:
    assert is_terminal(Delivered("x"))
    assert is_terminal(DeliveryFailed("x"))
    assert not is_terminal(InTransit("x"))


def test_assert_never_fails_at_runtime_for_a_foreign_object() -> None:
    with pytest.raises(AssertionError, match="Expected code to be unreachable"):
        describe("surprise")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"type": "booked", "reference": "BK-1"}, Booked("BK-1")),
        ({"type": "picked_up", "driver": "Ines", "extra": 1}, PickedUp("Ines")),
        (
            {"type": "in_transit", "location": {"name": "Rotterdam", "lat": 51.9}},
            InTransit("Rotterdam"),
        ),
        ({"type": "delivered", "signed_by": "A. Okafor"}, Delivered("A. Okafor")),
        ({"type": "failed", "reason": "no access"}, DeliveryFailed("no access")),
    ],
)
def test_mapping_patterns_ignore_extra_keys(
    payload: dict[str, Any], expected: TrackingEvent
) -> None:
    assert from_webhook(payload) == expected


def test_mapping_patterns_check_value_types_and_unknown_types() -> None:
    with pytest.raises(ValueError, match="unsupported webhook event 'lost'"):
        from_webhook({"type": "lost"})
    with pytest.raises(ValueError, match="unsupported webhook event 'booked'"):
        from_webhook({"type": "booked", "reference": 17})  # str(reference) rejects an int
    with pytest.raises(ValueError, match="no event type"):
        from_webhook({"reference": "BK-1"})


def test_sequence_patterns() -> None:
    assert summarize([]) == "no events"
    assert summarize([Booked("B")]) == "booked, nothing moved yet"
    history = (Booked("B"), PickedUp("I"), InTransit("R"), Delivered("A"))
    assert summarize(history) == "delivered after 2 events, signed by A"
    assert summarize([PickedUp("I"), DeliveryFailed("no access")]) == "failed: no access"
    assert summarize([PickedUp("I"), InTransit("R")]) == "PickedUp ... InTransit"
    assert summarize([InTransit("R")]) == "single event InTransit"


def test_sequence_patterns_do_not_match_str() -> None:
    text: Sequence[str] | str = "ab"
    match text:
        case [_, _]:
            matched = True
        case _:
            matched = False
    assert not matched


def _mypy(tmp_path: Path, source: str) -> tuple[str, int]:
    target = tmp_path / "snippet.py"
    target.write_text(textwrap.dedent(source))
    stdout, _stderr, status = mypy_api.run(["--strict", f"--cache-dir={os.devnull}", str(target)])
    return stdout.replace(str(target), "snippet.py"), status


DELIVERED_CASE = (
    '        case Delivered(signed_by):\n            return f"delivered, signed by {signed_by}"\n'
)
ALIAS = "type TrackingEvent = Booked | PickedUp | InTransit | Delivered | DeliveryFailed"


def test_mypy_strict_fails_when_a_case_is_removed(tmp_path: Path) -> None:
    source = Path(matching_module.__file__).read_text()
    assert DELIVERED_CASE in source
    complete, status = _mypy(tmp_path, source)
    assert status == 0, complete

    out, status = _mypy(tmp_path, source.replace(DELIVERED_CASE, ""))
    assert status == 1
    assert (
        'error: Argument 1 to "assert_never" has incompatible type "Delivered"; '
        'expected "Never"' in out
    ), out
    assert "Found 1 error" in out


def test_mypy_fails_when_a_new_event_joins_the_union(tmp_path: Path) -> None:
    source = Path(matching_module.__file__).read_text()
    widened = source.replace(
        ALIAS,
        "@dataclass(frozen=True)\nclass Returned:\n    to: str\n\n\n" + ALIAS + " | Returned",
    )
    assert widened != source
    out, status = _mypy(tmp_path, widened)
    assert status == 1
    assert out.count('has incompatible type "Returned"; expected "Never"') == 2, out
