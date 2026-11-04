"""A sailing manifest written so that a reader never sees a half-written file."""

import re
from collections.abc import Callable, Iterable, Iterator
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import NewType, TextIO

ConsignmentId = NewType("ConsignmentId", str)

_LOCODE = re.compile(r"[A-Z]{2}[A-Z0-9]{3}")

type Opener = Callable[[Path], TextIO]


@dataclass(frozen=True, slots=True)
class Manifest:
    """The consignments loaded on one sailing, bound for a UN/LOCODE port."""

    sailing: str
    port: str
    consignments: tuple[ConsignmentId, ...]

    def __post_init__(self) -> None:
        if not _LOCODE.fullmatch(self.port):
            raise ValueError(f"port must look like NLRTM, got {self.port!r}")


def open_utf8(path: Path) -> TextIO:
    """Open a path for writing text. The encoding is explicit, whatever the platform default."""
    return path.open("w", encoding="utf-8")


def render_line(consignment_id: ConsignmentId) -> str:
    return f"{consignment_id}\n"


def _partial(path: Path) -> Path:
    return path.with_name(f"{path.name}.partial")


class ManifestWriter:
    """Write to `<name>.partial`; commit it to `<name>` only if the block succeeds."""

    def __init__(self, path: Path, *, opener: Opener = open_utf8) -> None:
        self._path = path
        self._partial = _partial(path)
        self._opener = opener
        self._handle: TextIO | None = None
        self._entered = False

    def __enter__(self) -> TextIO:
        if self._entered:
            raise RuntimeError("ManifestWriter is single-use")
        self._entered = True
        self._handle = self._opener(self._partial)
        return self._handle

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._handle is None:
            raise RuntimeError("ManifestWriter was not entered")
        if exc_type is None:
            self._handle.close()
            self._partial.replace(self._path)
        else:
            self._handle.close()
            self._partial.unlink(missing_ok=True)


@contextmanager
def manifest_file(path: Path, *, opener: Opener = open_utf8) -> Iterator[TextIO]:
    """The same contract as `ManifestWriter`, written as a generator."""
    partial = _partial(path)
    handle = opener(partial)
    try:
        yield handle
    except BaseException:
        handle.close()
        partial.unlink(missing_ok=True)
        raise
    else:
        handle.close()
        partial.replace(path)


def write_manifests(
    manifests: Iterable[Manifest], directory: Path, *, opener: Opener = open_utf8
) -> list[Path]:
    """Write every manifest or none: a failure discards the partials of all those entered."""
    paths: list[Path] = []
    with ExitStack() as stack:
        for manifest in manifests:
            path = directory / f"{manifest.sailing}-{manifest.port}.manifest"
            out = stack.enter_context(ManifestWriter(path, opener=opener))
            out.writelines(render_line(c) for c in manifest.consignments)
            paths.append(path)
    return paths
