import functools
import gc
import weakref
from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest
from decorators_done_right.rendering import timed_render

if TYPE_CHECKING:
    from conftest import FakeClock, Timings


class _ClassWrapper[**P, R]:
    """A class-based wrapper. It has ``__call__`` but, unlike a function, no ``__get__``."""

    def __init__(self, func: Callable[P, R]) -> None:
        self._func = func
        functools.update_wrapper(self, func)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self._func(*args, **kwargs)


def test_a_function_wrapper_binds_self_on_a_method(clock: FakeClock, timings: Timings) -> None:
    class Renderer:
        prefix = "Bill of lading"

        @timed_render(timings, clock=clock)
        def render(self, number: str) -> str:
            return f"{self.prefix} {number}"

    assert Renderer().render("BL-1") == "Bill of lading BL-1"
    assert timings.records == [("render", 0.0)]


def test_a_class_based_wrapper_does_not_bind_self() -> None:
    class Renderer:
        prefix = "Bill of lading"

        @_ClassWrapper
        def render(self, number: str) -> str:
            return f"{self.prefix} {number}"

    with pytest.raises(TypeError, match="missing 1 required positional argument"):
        Renderer().render("BL-1")  # type: ignore[arg-type, call-arg]


def test_functools_cache_on_a_method_keeps_the_instance_alive() -> None:
    class Renderer:
        @functools.cache  # noqa: B019
        def render(self, number: str) -> str:
            return f"Bill of lading {number}"

    renderer = Renderer()
    renderer.render("BL-1")
    reference = weakref.ref(renderer)

    # The cache holds a strong reference to the instance as part of its key. gc.collect() is
    # explicit so the assertions do not depend on when CPython frees an object by reference count.
    del renderer
    gc.collect()
    assert reference() is not None

    Renderer.render.cache_clear()
    gc.collect()
    assert reference() is None
