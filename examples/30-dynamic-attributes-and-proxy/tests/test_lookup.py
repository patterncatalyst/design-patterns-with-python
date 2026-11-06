import copy
import pickle
import traceback
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING

import pytest
from dynamic_attributes.tracking import (
    ConsignmentId,
    ConsignmentStatus,
    TrackingHistory,
)

if TYPE_CHECKING:
    from conftest import RecordingLoad

_FIXES = ["allow-list", "object-getattribute", "vars"]


def _read(target: object, name: str) -> object:
    return getattr(target, name)


def _load_by_name(name: str) -> str:
    """A module-level loader, so that ``pickle`` can store it by reference.

    It knows one field. A loader that answered every name would make ``deepcopy`` fail on the
    string it gets back for ``__deepcopy__``, before it reached the recursion.
    """
    if name != "events":
        raise AttributeError(name)
    return "loaded events"


class _SelfHealing:
    """The trap: ``__getattr__`` reads ``self._load``, which is missing on a bare instance."""

    def __init__(self, load: Callable[[str], str]) -> None:
        self._load = load

    def __getattr__(self, name: str) -> object:
        value = self._load(name)
        vars(self)[name] = value
        return value


class _ObjectGetattribute:
    """Fix: read the loader without going through ``__getattr__``."""

    def __getattr__(self, name: str) -> object:
        load: Callable[[str], str] = object.__getattribute__(self, "_load")
        return load(name)


class _Vars:
    """Fix: read the loader from the instance dictionary."""

    def __getattr__(self, name: str) -> object:
        load = vars(self).get("_load")
        if load is None:
            raise AttributeError(name)
        return load(name)


class _Forgiving:
    """A ``__getattr__`` that answers every name from a mapping."""

    def __init__(self) -> None:
        self._fields = {"status": "in transit"}

    def __getattr__(self, name: str) -> object:
        return self._fields.get(name)


class _Forwarding:
    """Forwards missing names to a tuple and logs each one that reaches the hook."""

    def __init__(self, inner: tuple[str, ...], seen: list[str]) -> None:
        self._inner = inner
        self._seen = seen

    def __getattr__(self, name: str) -> object:
        self._seen.append(name)
        return getattr(self._inner, name)


def test_getattr_runs_only_when_normal_lookup_fails(recording_load: RecordingLoad) -> None:
    seen: list[str] = []

    class Counting(TrackingHistory):
        def __getattr__(self, name: str) -> object:
            seen.append(name)
            return super().__getattr__(name)

    history = Counting(ConsignmentId("CN-1"), recording_load)
    for _ in range(3):
        assert history.status is ConsignmentStatus.IN_TRANSIT
    assert history.consignment_id == "CN-1"
    assert seen == ["status"]


def test_getattribute_runs_on_every_access(recording_load: RecordingLoad) -> None:
    seen: list[str] = []

    class Counting(TrackingHistory):
        def __getattribute__(self, name: str) -> object:
            seen.append(name)
            return super().__getattribute__(name)

    history = Counting(ConsignmentId("CN-1"), recording_load)
    assert history.consignment_id == "CN-1"
    assert seen == ["consignment_id"]
    for _ in range(3):
        assert history.status is ConsignmentStatus.IN_TRANSIT
    assert seen.count("status") == 3


def test_a_getattr_that_reads_a_missing_attribute_recurses() -> None:
    bare = _SelfHealing.__new__(_SelfHealing)
    with pytest.raises(RecursionError):
        _read(bare, "events")


def _through_pickle(original: _SelfHealing) -> _SelfHealing:
    twin: _SelfHealing = pickle.loads(pickle.dumps(original))
    return twin


@pytest.mark.parametrize(
    "duplicate",
    [copy.copy, copy.deepcopy, _through_pickle],
    ids=["copy", "deepcopy", "pickle"],
)
def test_copy_recurses_through_a_getattr_that_reads_a_missing_attribute(
    duplicate: Callable[[_SelfHealing], _SelfHealing],
) -> None:
    original = _SelfHealing(_load_by_name)
    with pytest.raises(RecursionError):
        duplicate(original)


def test_copy_keeps_a_history_before_and_after_loading(recording_load: RecordingLoad) -> None:
    unloaded = TrackingHistory(ConsignmentId("CN-1"), recording_load)
    for duplicate in (copy.copy, copy.deepcopy):
        twin = duplicate(unloaded)
        assert sorted(vars(twin)) == ["_load", "consignment_id"]
    assert recording_load.calls == []

    loaded = TrackingHistory(ConsignmentId("CN-1"), recording_load)
    assert loaded.status is ConsignmentStatus.IN_TRANSIT
    for duplicate in (copy.copy, copy.deepcopy):
        twin = duplicate(loaded)
        assert twin.events == loaded.events
        assert twin.status is ConsignmentStatus.IN_TRANSIT
    assert recording_load.calls == ["CN-1"]


@pytest.mark.parametrize("fix", [TrackingHistory, _ObjectGetattribute, _Vars], ids=_FIXES)
def test_each_fix_keeps_getattr_out_of_recursion(
    fix: type[TrackingHistory | _ObjectGetattribute | _Vars],
) -> None:
    bare = fix.__new__(fix)
    assert type(copy.copy(bare)) is fix
    with pytest.raises(AttributeError):
        _read(bare, "events")


def test_a_getattr_that_returns_none_hides_a_typo() -> None:
    forgiving = _Forgiving()
    assert _read(forgiving, "status") == "in transit"
    assert _read(forgiving, "stauts") is None


def test_implicit_special_method_lookup_bypasses_getattr() -> None:
    seen: list[str] = []
    forwarding = _Forwarding(("e1", "e2"), seen)

    explicit = _read(forwarding, "__iter__")
    assert callable(explicit)
    iterator = explicit()
    assert isinstance(iterator, Iterator)
    assert list(iterator) == ["e1", "e2"]
    assert seen == ["__iter__"]

    seen.clear()
    with pytest.raises(TypeError, match="is not iterable"):
        iter(forwarding)  # type: ignore[call-overload]
    with pytest.raises(TypeError, match="has no len"):
        len(forwarding)  # type: ignore[arg-type]
    assert seen == []


def test_dir_lists_the_lazy_fields_before_loading(recording_load: RecordingLoad) -> None:
    history = TrackingHistory(ConsignmentId("CN-1"), recording_load)
    assert {"events", "last_port", "status"} <= set(dir(history))
    assert recording_load.calls == []


def _hint(history: object) -> str:
    with pytest.raises(AttributeError) as caught:
        _read(history, "stauts")
    return "".join(traceback.format_exception_only(caught.value))


def test_a_misspelt_field_suggests_the_declared_name_through_dir(
    recording_load: RecordingLoad,
) -> None:
    class Undeclared(TrackingHistory):
        def __dir__(self) -> list[str]:
            return list(object.__dir__(self))

    hinted = _hint(TrackingHistory(ConsignmentId("CN-1"), recording_load))
    unhinted = _hint(Undeclared(ConsignmentId("CN-1"), recording_load))
    assert hinted.rstrip().endswith("Did you mean '.status' instead of '.stauts'?")
    assert "Did you mean" not in unhinted
    assert recording_load.calls == []


def test_hasattr_loads_the_history(recording_load: RecordingLoad) -> None:
    history = TrackingHistory(ConsignmentId("CN-1"), recording_load)
    assert hasattr(history, "status")
    assert recording_load.calls == ["CN-1"]
