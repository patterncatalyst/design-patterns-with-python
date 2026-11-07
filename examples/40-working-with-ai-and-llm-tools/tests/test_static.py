"""What mypy reports when an assistant has no ``reply``."""

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


# A client with `answer` where the Protocol asks for `reply`, passed to the review loop.
_NO_REPLY = """
from review_gate.assistant import propose


class Answers:
    def answer(self, prompt: str, /) -> str:
        return prompt


propose("price it", assistant=Answers(), gates=[])
"""
_WITH_REPLY = _NO_REPLY.replace("def answer", "def reply")


def test_mypy_refuses_an_assistant_without_reply(tmp_path: Path) -> None:
    """Credits the ``Assistant`` annotation on ``propose``: annotating ``assistant`` as ``object``
    makes the first list empty, and ``src`` then reports ``attr-defined``."""
    bare, bare_status = _run(_NO_REPLY, tmp_path)
    complete, complete_status = _run(_WITH_REPLY, tmp_path)

    assert [_codes(bare), _codes(complete)] == [["arg-type"], []]
    assert (bare_status, complete_status) == (1, 0)
    assert "Assistant" in bare
