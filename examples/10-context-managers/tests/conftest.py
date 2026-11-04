import io
from collections.abc import Callable
from pathlib import Path

import pytest
from context_managers.manifest import ConsignmentId, Manifest


class RecordedFile(io.TextIOWrapper):
    """A real UTF-8 text file that appends its path to a list when it is first closed."""

    def __init__(self, path: Path, closed: list[Path]) -> None:
        super().__init__(path.open("wb"), encoding="utf-8")
        self._path = path
        self._closed = closed

    def close(self) -> None:
        if not self.closed:
            self._closed.append(self._path)
        super().close()


class RecordingOpener:
    """An `Opener` that records opens and closes in order and can fail on the Nth open."""

    def __init__(self, *, fail_on: int | None = None) -> None:
        self.opened: list[Path] = []
        self.closed: list[Path] = []
        self.files: list[RecordedFile] = []
        self._fail_on = fail_on

    def __call__(self, path: Path) -> RecordedFile:
        if self._fail_on is not None and len(self.opened) + 1 == self._fail_on:
            raise OSError("simulated open failure")
        file = RecordedFile(path, self.closed)
        self.opened.append(path)
        self.files.append(file)
        return file


@pytest.fixture
def opener() -> RecordingOpener:
    return RecordingOpener()


@pytest.fixture
def opener_failing_on() -> Callable[[int], RecordingOpener]:
    def make(n: int) -> RecordingOpener:
        return RecordingOpener(fail_on=n)

    return make


@pytest.fixture
def manifests() -> list[Manifest]:
    return [
        Manifest("SL-0001", "NLRTM", (ConsignmentId("CN-00000001"), ConsignmentId("CN-00000002"))),
        Manifest("SL-0001", "SGSIN", (ConsignmentId("CN-00000003"),)),
        Manifest("SL-0001", "DEHAM", (ConsignmentId("CN-00000004"),)),
    ]
