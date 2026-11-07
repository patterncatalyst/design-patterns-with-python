"""The model client as a dependency: a Protocol, a recorded fake and a review loop."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol

from review_gate.shape import Finding


class Assistant(Protocol):
    def reply(self, prompt: str, /) -> str: ...


class RecordedAssistant:
    """Replays recorded replies in order for each prompt and refuses a prompt without one."""

    def __init__(self, replies: Mapping[str, Sequence[str]]) -> None:
        self._replies = {prompt: list(texts) for prompt, texts in replies.items()}
        self.prompts: list[str] = []

    def reply(self, prompt: str, /) -> str:
        self.prompts.append(prompt)
        remaining = self._replies.get(prompt)
        if not remaining:
            raise LookupError(f"no recorded reply for prompt {prompt!r}")
        return remaining.pop(0)


type Gate = Callable[[str], list[Finding]]


@dataclass(frozen=True, slots=True)
class Review:
    source: str
    findings: tuple[Finding, ...]

    @property
    def accepted(self) -> bool:
        return not self.findings


def propose(
    prompt: str, /, *, assistant: Assistant, gates: Sequence[Gate], attempts: int = 2
) -> list[Review]:
    """Ask, gate the reply and, if it is rejected, ask again with the findings appended."""
    reviews: list[Review] = []
    current = prompt
    for _ in range(attempts):
        source = assistant.reply(current)
        findings = tuple(finding for gate in gates for finding in gate(source))
        reviews.append(Review(source, findings))
        if not findings:
            break
        lines = "\n".join(f"line {f.line}: {f.rule}, {f.advice}" for f in findings)
        current = f"{prompt}\n\nFix these findings:\n{lines}"
    return reviews
