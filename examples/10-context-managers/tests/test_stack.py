from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from context_managers.manifest import Manifest, write_manifests

if TYPE_CHECKING:
    from conftest import RecordingOpener


def test_exit_stack_unwinds_entered_writers_in_reverse_order(
    tmp_path: Path,
    manifests: list[Manifest],
    opener_failing_on: Callable[[int], RecordingOpener],
) -> None:
    opener = opener_failing_on(3)
    with pytest.raises(OSError, match="simulated open failure"):
        write_manifests(manifests, tmp_path, opener=opener)
    first = tmp_path / "SL-0001-NLRTM.manifest.partial"
    second = tmp_path / "SL-0001-SGSIN.manifest.partial"
    assert opener.opened == [first, second]
    assert opener.closed == [second, first]
    assert list(tmp_path.iterdir()) == []


def test_exit_stack_commits_every_manifest_on_success(
    tmp_path: Path, manifests: list[Manifest], opener: RecordingOpener
) -> None:
    paths = write_manifests(manifests, tmp_path, opener=opener)
    assert [p.name for p in paths] == [
        "SL-0001-NLRTM.manifest",
        "SL-0001-SGSIN.manifest",
        "SL-0001-DEHAM.manifest",
    ]
    assert paths[0].read_text(encoding="utf-8") == "CN-00000001\nCN-00000002\n"
    assert paths[2].read_text(encoding="utf-8") == "CN-00000004\n"
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(p.name for p in paths)
    assert len(opener.closed) == 3
