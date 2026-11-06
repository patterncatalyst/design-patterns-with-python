import functools
import inspect
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Concatenate

import pytest
from decorators_done_right.domain import BillOfLading, ConsignmentId
from decorators_done_right.rendering import Clock, cached_for, render_bill, timed_render

if TYPE_CHECKING:
    from conftest import FakeClock, Timings, WrapperForm

_ORIGINAL_SIGNATURE = (
    "(bill: decorators_done_right.domain.BillOfLading, /, *, width: int = 72) -> str"
)


def _signature_text(func: Callable[..., object]) -> str:
    return str(inspect.signature(func))


@pytest.mark.parametrize(
    "bill",
    [
        BillOfLading("BL-1", ConsignmentId("CN-1"), "NLRTM", "SGSIN"),
        BillOfLading("BL-2", ConsignmentId("CN-2"), "DEHAM", "NLRTM"),
    ],
    ids=["first-bill", "second-bill"],
)
def test_both_wrapper_forms_render_the_same_text(
    wrapper_form: WrapperForm, bill: BillOfLading
) -> None:
    timed = wrapper_form(render_bill)

    assert timed(bill) == render_bill(bill)
    assert timed(bill, width=30) == render_bill(bill, width=30)


def test_render_bill_shortens_the_line_to_the_width(bill: BillOfLading) -> None:
    line = render_bill(bill, width=30)

    assert len(line) <= 30
    assert line.endswith("...")
    assert render_bill(bill) == ("Bill of lading BL-1: consignment CN-1 from NLRTM to SGSIN")


def test_wraps_keeps_the_name_qualname_doc_and_module(timer: WrapperForm) -> None:
    timed = timer(render_bill)

    assert timed.__name__ == "render_bill"
    assert timed.__qualname__ == "render_bill"
    assert timed.__doc__ == render_bill.__doc__
    assert timed.__doc__ is not None
    assert timed.__module__ == render_bill.__module__


def test_a_wrapper_without_wraps_reports_its_own_name_and_no_docstring(
    bare_timer: WrapperForm,
) -> None:
    timed = bare_timer(render_bill)

    assert timed.__name__ == "wrapper"
    assert timed.__qualname__.endswith("<locals>.wrapper")
    assert timed.__doc__ is None
    assert timed.__module__ != render_bill.__module__
    assert not hasattr(timed, "__wrapped__")


def test_inspect_signature_follows_wrapped_to_the_original_parameters(
    timer: WrapperForm, bare_timer: WrapperForm
) -> None:
    assert _signature_text(timer(render_bill)) == _ORIGINAL_SIGNATURE
    assert _signature_text(render_bill) == _ORIGINAL_SIGNATURE
    assert _signature_text(bare_timer(render_bill)) == "(*args: P.args, **kwargs: P.kwargs) -> R"


def test_wraps_copies_the_function_dict_and_adds_wrapped(timer: WrapperForm) -> None:
    def render(bill: BillOfLading, /) -> str:
        return render_bill(bill)

    render.__dict__["kind"] = "BILL_OF_LADING"
    timed = timer(render)
    copied: Mapping[str, object] = timed.__dict__

    assert copied == {"kind": "BILL_OF_LADING", "__wrapped__": render}


def test_wrapped_points_one_level_down_and_unwrap_reaches_the_original(
    timings: Timings, clock: FakeClock
) -> None:
    cached = cached_for(seconds=60, clock=clock)(render_bill)
    outer = timed_render(timings, clock=clock)(cached)

    assert outer.__wrapped__ is cached  # type: ignore[attr-defined]
    assert cached.__wrapped__ is render_bill
    assert inspect.unwrap(outer) is render_bill


def test_wraps_copies_annotate_rather_than_annotations(
    timer: WrapperForm, bare_timer: WrapperForm
) -> None:
    # PEP 749: since 3.14 the copied attribute is __annotate__. The functools page still lists
    # __annotations__, so this test reads the constant the interpreter really uses.
    assert "__annotate__" in functools.WRAPPER_ASSIGNMENTS
    assert "__annotations__" not in functools.WRAPPER_ASSIGNMENTS
    assert timer(render_bill).__annotations__ == render_bill.__annotations__
    assert bare_timer(render_bill).__annotations__ != render_bill.__annotations__


def issued_at(clock: Clock, number: str, /) -> str:
    return f"{number} issued at {clock():.0f}"


def supplying[**P, R](
    clock: Clock,
) -> Callable[[Callable[Concatenate[Clock, P], R]], Callable[P, R]]:
    """Supply the first argument. ``wraps`` assumes the wrapper takes the same arguments."""

    def decorate(func: Callable[Concatenate[Clock, P], R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(clock, *args, **kwargs)

        return wrapper

    return decorate


def test_a_decorator_that_supplies_an_argument_reports_the_original_parameters(
    clock: FakeClock,
) -> None:
    stamp = supplying(clock)(issued_at)
    signature = inspect.signature(stamp)

    assert stamp("BL-1") == "BL-1 issued at 1000"
    assert list(signature.parameters) == ["clock", "number"]
    with pytest.raises(TypeError, match="missing a required argument"):
        signature.bind("BL-1")


def test_partial_reports_the_parameters_that_remain(clock: FakeClock) -> None:
    stamp = functools.partial(issued_at, clock)
    signature = inspect.signature(stamp)

    assert stamp("BL-1") == "BL-1 issued at 1000"
    assert list(signature.parameters) == ["number"]
    assert signature.bind("BL-1").arguments == {"number": "BL-1"}
