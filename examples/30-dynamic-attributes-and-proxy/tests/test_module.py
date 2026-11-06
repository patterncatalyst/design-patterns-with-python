import pytest
from dynamic_attributes import tracking
from dynamic_attributes.tracking import TrackingHistory


def _read(target: object, name: str) -> object:
    return getattr(target, name)


def test_a_deprecated_name_warns_and_returns_the_tracking_history() -> None:
    with pytest.warns(
        DeprecationWarning, match="LazyTrackingHistory is deprecated; use TrackingHistory"
    ) as record:
        alias = tracking.LazyTrackingHistory
    assert alias is TrackingHistory
    assert record[0].filename == __file__


def test_an_unknown_module_attribute_raises_attribute_error() -> None:
    with pytest.raises(
        AttributeError, match=r"module 'dynamic_attributes\.tracking' has no attribute 'Missing'"
    ):
        _read(tracking, "Missing")


def test_module_dir_lists_the_deprecated_name() -> None:
    assert "LazyTrackingHistory" in dir(tracking)
    assert "TrackingHistory" in dir(tracking)
