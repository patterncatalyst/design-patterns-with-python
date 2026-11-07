"""A coroutine is a value until it is awaited, and the runtime warns when one is dropped."""

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from asyncio_patterns.domain import Consignment, ConsignmentId
from asyncio_patterns.quoting import FastlineSource

if TYPE_CHECKING:
    from conftest import Runner

CONSIGNMENT = Consignment(ConsignmentId("CN-1"), "EU", Decimal("20"))


def test_calling_a_coroutine_function_without_await_gives_a_coroutine_not_a_quote(
    run: Runner,
) -> None:
    coroutine = FastlineSource().quote(CONSIGNMENT)
    kind = type(coroutine).__name__

    quote = run(coroutine)

    assert (kind, quote.carrier) == ("coroutine", "FASTLINE")


def test_a_quote_that_is_never_awaited_warns_when_it_is_collected() -> None:
    """Relies on CPython freeing the coroutine as soon as its last reference goes."""
    source = FastlineSource()

    def forget() -> None:
        coroutine = source.quote(CONSIGNMENT)
        del coroutine

    with pytest.warns(RuntimeWarning) as record:
        forget()

    assert [str(warning.message) for warning in record] == [
        "coroutine 'FastlineSource.quote' was never awaited"
    ]
