from collections.abc import Iterator
from contextlib import contextmanager, suppress
from types import TracebackType

import pytest
from context_managers.manifest import ConsignmentId, Manifest


class _Swallowing:
    """A context manager whose `__exit__` returns a truthy value for every exception."""

    def __enter__(self) -> None:
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        return True


def test_a_truthy_exit_swallows_the_exception() -> None:
    reached = False
    with _Swallowing():
        raise ValueError("lost")
    reached = True
    assert reached


def test_suppress_swallows_only_the_named_exception() -> None:
    with suppress(KeyError):
        raise KeyError("expected")
    with pytest.raises(ValueError, match="other"), suppress(KeyError):
        raise ValueError("other")


def test_a_context_manager_decorating_a_generator_spans_iteration() -> None:
    """Python 3.15 behaviour. Before 3.15 the log was ["enter", "exit", "row NLRTM", ...]."""
    log: list[str] = []

    @contextmanager
    def scope() -> Iterator[None]:
        log.append("enter")
        try:
            yield
        finally:
            log.append("exit")

    @scope()
    def rows() -> Iterator[str]:
        for port in ("NLRTM", "SGSIN"):
            log.append(f"row {port}")
            yield port

    iterator = rows()
    assert log == []
    assert list(iterator) == ["NLRTM", "SGSIN"]
    assert log == ["enter", "row NLRTM", "row SGSIN", "exit"]


@pytest.mark.parametrize("port", ["nlrtm", "NLRT", "NLRTMX", "NL-TM", ""])
def test_manifest_rejects_a_port_that_is_not_a_locode(port: str) -> None:
    with pytest.raises(ValueError, match="port must look like NLRTM"):
        Manifest("SL-0001", port, (ConsignmentId("CN-00000001"),))


def test_manifest_accepts_a_locode() -> None:
    assert Manifest("SL-0001", "NLRTM", ()).port == "NLRTM"
