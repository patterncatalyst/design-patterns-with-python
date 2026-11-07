"""The model client behind a Protocol: a recorded fake and the review loop, with no network."""

import ast
from collections.abc import Mapping
from pathlib import Path

import pytest
from review_gate.assistant import RecordedAssistant, propose
from review_gate.shape import review

_PACKAGE = Path(__file__).resolve().parents[1] / "src" / "review_gate"
_NETWORK = {"socket", "ssl", "http", "urllib", "asyncio", "subprocess"}

_PROMPT = "Write price() over PricingRule."
_FIX_UP = (
    "Write price() over PricingRule.\n\n"
    "Fix these findings:\n"
    "line 8: single-method-base, use a callable type alias\n"
    "line 27: static-only-class, use module-level functions"
)


def test_a_rejected_reply_is_sent_back_with_its_findings(drafts: Mapping[str, str]) -> None:
    assistant = RecordedAssistant(
        {_PROMPT: [drafts["typed_hierarchy"]], _FIX_UP: [drafts["rounded_callable"]]}
    )

    reviews = propose(_PROMPT, assistant=assistant, gates=[review])

    assert (assistant.prompts, [r.accepted for r in reviews]) == ([_PROMPT, _FIX_UP], [False, True])


def test_the_loop_stops_at_the_first_accepted_reply(drafts: Mapping[str, str]) -> None:
    assistant = RecordedAssistant(
        {_PROMPT: [drafts["rounded_callable"], drafts["typed_hierarchy"]]}
    )

    reviews = propose(_PROMPT, assistant=assistant, gates=[review])

    assert (assistant.prompts, [r.accepted for r in reviews]) == ([_PROMPT], [True])


def test_the_loop_gives_up_after_its_attempts(drafts: Mapping[str, str]) -> None:
    typed = drafts["typed_hierarchy"]
    assistant = RecordedAssistant({_PROMPT: [typed], _FIX_UP: [typed]})

    reviews = propose(_PROMPT, assistant=assistant, gates=[review], attempts=2)

    assert (assistant.prompts, [r.accepted for r in reviews]) == (
        [_PROMPT, _FIX_UP],
        [False, False],
    )


def test_an_unrecorded_prompt_is_refused() -> None:
    assistant = RecordedAssistant({_PROMPT: ["reply"]})

    with pytest.raises(LookupError, match="no recorded reply for prompt 'Something else'"):
        assistant.reply("Something else")


def test_the_package_imports_no_network_module() -> None:
    scanned: list[str] = []
    imported: list[str] = []
    for path in sorted(_PACKAGE.glob("*.py")):
        scanned.append(path.name)
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                imported += [f"{path.name}: {a.name}" for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(f"{path.name}: {node.module}")

    offenders = [i for i in imported if i.split(": ")[1].split(".")[0] in _NETWORK]
    assert (scanned, offenders) == (
        ["__init__.py", "assistant.py", "domain.py", "pricing.py", "shape.py"],
        [],
    )
