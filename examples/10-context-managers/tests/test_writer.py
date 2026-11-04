from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, TextIO

import pytest
from context_managers.manifest import (
    ConsignmentId,
    ManifestWriter,
    Opener,
    manifest_file,
    render_line,
)

if TYPE_CHECKING:
    from conftest import RecordingOpener


class _Form(Protocol):
    def __call__(self, path: Path, /, *, opener: Opener) -> AbstractContextManager[TextIO]: ...


_FORMS = [pytest.param(ManifestWriter, id="class"), pytest.param(manifest_file, id="generator")]

_ID = ConsignmentId("CN-00000001")


def _fail_midwrite(form: _Form, path: Path, opener: Opener) -> None:
    """Enter a manager, write a line, then fail inside the block."""
    with form(path, opener=opener) as out:
        out.write(render_line(_ID))
        raise OSError("disk full")


def _write_without_with(path: Path, opener: Opener) -> None:
    """The mistake: acquire, write, fail, and never release."""
    handle = opener(path)
    handle.write(render_line(_ID))
    raise OSError("disk full")


@contextmanager
def _leaky_manifest_file(path: Path, *, opener: Opener) -> Iterator[TextIO]:
    """A generator-form manager with no `try`: the code after `yield` never runs on an error."""
    partial = path.with_name(f"{path.name}.partial")
    handle = opener(partial)
    yield handle
    handle.close()
    partial.replace(path)


def test_without_with_an_exception_leaves_the_handle_open(
    tmp_path: Path, opener: RecordingOpener
) -> None:
    path = tmp_path / "plain.partial"
    try:
        with pytest.raises(OSError, match="disk full"):
            _write_without_with(path, opener)
        assert opener.closed == []
        assert not opener.files[0].closed
    finally:
        opener.files[0].close()


@pytest.mark.parametrize("form", _FORMS)
def test_writer_closes_and_discards_on_an_exception(
    form: _Form, tmp_path: Path, opener: RecordingOpener
) -> None:
    path = tmp_path / "SL-0001-NLRTM.manifest"
    partial = tmp_path / "SL-0001-NLRTM.manifest.partial"
    with pytest.raises(OSError, match="disk full"):
        _fail_midwrite(form, path, opener)
    assert opener.files[0].closed
    assert opener.closed == [partial]
    assert not partial.exists()
    assert not path.exists()


@pytest.mark.parametrize("form", _FORMS)
def test_writer_commits_only_on_success(
    form: _Form, tmp_path: Path, opener: RecordingOpener
) -> None:
    path = tmp_path / "SL-0001-NLRTM.manifest"
    partial = tmp_path / "SL-0001-NLRTM.manifest.partial"
    with form(path, opener=opener) as out:
        out.write(render_line(_ID))
        assert not path.exists()
        assert partial.exists()
    assert opener.files[0].closed
    assert opener.closed == [partial]
    assert path.read_text(encoding="utf-8") == "CN-00000001\n"
    assert not partial.exists()


def test_writer_is_single_use(tmp_path: Path, opener: RecordingOpener) -> None:
    writer = ManifestWriter(tmp_path / "once.manifest", opener=opener)
    with writer:
        pass
    with pytest.raises(RuntimeError, match="single-use"), writer:
        pass
    assert len(opener.opened) == 1


def test_exiting_a_writer_that_was_never_entered_is_refused(tmp_path: Path) -> None:
    writer = ManifestWriter(tmp_path / "never.manifest")
    with pytest.raises(RuntimeError, match="was not entered"):
        writer.__exit__(None, None, None)


def test_the_generator_form_needs_try(tmp_path: Path, opener: RecordingOpener) -> None:
    path = tmp_path / "leaky.manifest"
    partial = tmp_path / "leaky.manifest.partial"
    try:
        with pytest.raises(OSError, match="disk full"):
            _fail_midwrite(_leaky_manifest_file, path, opener)
        assert not opener.files[0].closed
        assert opener.closed == []
        assert partial.exists()
        assert not path.exists()
    finally:
        opener.files[0].close()
