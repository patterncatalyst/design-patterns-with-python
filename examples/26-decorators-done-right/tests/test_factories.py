import re
from typing import TYPE_CHECKING

import pytest
from decorators_done_right.domain import BillOfLading
from decorators_done_right.rendering import cached_for, render_bill, timed_render

if TYPE_CHECKING:
    from conftest import FakeClock, PositionalFactory, Timings

WINDOW = 300.0


class Renders:
    """A renderer that counts its calls and takes two seconds of clock time to run."""

    def __init__(self, clock: FakeClock) -> None:
        self.calls = 0
        self._clock = clock

    def __call__(self, bill: BillOfLading, /, *, width: int = 72) -> str:
        self.calls += 1
        self._clock.advance(2)
        return render_bill(bill, width=width)


def test_cached_for_returns_the_cached_text_within_the_window(
    bill: BillOfLading, clock: FakeClock
) -> None:
    renders = Renders(clock)
    cached = cached_for(seconds=WINDOW, clock=clock)(renders)

    first = cached(bill)
    clock.advance(WINDOW - 3)
    second = cached(bill)

    assert second == first
    assert renders.calls == 1


@pytest.mark.parametrize("elapsed", [WINDOW, WINDOW + 1], ids=["at-the-limit", "past-it"])
def test_cached_for_renders_again_once_the_window_has_passed(
    bill: BillOfLading, clock: FakeClock, elapsed: float
) -> None:
    renders = Renders(clock)
    cached = cached_for(seconds=WINDOW, clock=clock)(renders)

    cached(bill)
    clock.advance(elapsed - 2)  # the render itself took two seconds of the window
    cached(bill)

    assert renders.calls == 2


def test_cached_for_keeps_one_entry_per_argument(bill: BillOfLading, clock: FakeClock) -> None:
    other = BillOfLading("BL-2", bill.consignment_id, "DEHAM", "NLRTM")
    renders = Renders(clock)
    cached = cached_for(seconds=WINDOW, clock=clock)(renders)

    assert cached(bill) == render_bill(bill)
    assert cached(other) == render_bill(other)
    assert cached(bill, width=30) == render_bill(bill, width=30)
    assert renders.calls == 3
    assert cached(bill) == render_bill(bill)
    assert cached(other) == render_bill(other)
    assert cached(bill, width=30) == render_bill(bill, width=30)
    assert renders.calls == 3


def test_cached_for_refuses_an_unhashable_argument(clock: FakeClock) -> None:
    def render(numbers: list[str], /) -> str:
        return ", ".join(numbers)

    cached = cached_for(seconds=WINDOW, clock=clock)(render)

    message = "cannot use 'tuple' as a dict key (unhashable type: 'list')"
    with pytest.raises(TypeError, match=re.escape(message)):
        cached(["BL-1"])


@pytest.mark.parametrize("seconds", [0, -5], ids=["zero", "negative"])
def test_cached_for_refuses_a_window_that_is_not_positive(seconds: float) -> None:
    with pytest.raises(ValueError, match="seconds must be positive"):
        cached_for(seconds=seconds)


@pytest.mark.parametrize("fails", [False, True], ids=["rendered", "raised"])
def test_timed_render_reports_the_elapsed_clock_time(
    bill: BillOfLading, clock: FakeClock, timings: Timings, fails: bool
) -> None:
    @timed_render(timings, clock=clock)
    def render(bill: BillOfLading, /) -> str:
        clock.advance(2)
        if fails:
            raise RuntimeError("renderer down")
        return render_bill(bill)

    if fails:
        with pytest.raises(RuntimeError, match="renderer down"):
            render(bill)
    else:
        render(bill)

    assert timings.records == [("render", 2.0)]


def test_a_positional_factory_used_bare_binds_the_name_to_its_inner_decorator(
    bill: BillOfLading, positional_factory: PositionalFactory
) -> None:
    @positional_factory  # type: ignore[arg-type]
    def render(bill: BillOfLading, /) -> str:
        return render_bill(bill)

    result = render(bill)  # type: ignore[arg-type]

    assert render.__name__ == "decorate"
    assert callable(result)
    assert not isinstance(result, str)
    assert result.__name__ == "wrapper"


def test_a_keyword_only_factory_used_bare_fails_at_definition() -> None:
    with pytest.raises(TypeError, match="takes 0 positional arguments"):

        @cached_for  # type: ignore[call-arg, arg-type]
        def render(bill: BillOfLading, /) -> str:
            return render_bill(bill)


@pytest.mark.parametrize(
    ("timer_outside", "expected"),
    [(True, [("render", 2.0), ("render", 0.0)]), (False, [("render", 2.0)])],
    ids=["timer-outside-2", "timer-inside-1"],
)
def test_stacking_order_decides_whether_a_cache_hit_is_timed(
    bill: BillOfLading,
    clock: FakeClock,
    timings: Timings,
    timer_outside: bool,
    expected: list[tuple[str, float]],
) -> None:
    renders = Renders(clock)

    def render(bill: BillOfLading, /) -> str:
        return renders(bill)

    cache = cached_for(seconds=WINDOW, clock=clock)
    timer = timed_render(timings, clock=clock)
    stacked = timer(cache(render)) if timer_outside else cache(timer(render))

    stacked(bill)
    stacked(bill)

    assert renders.calls == 1
    assert timings.records == expected
