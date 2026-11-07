"""Quoting with several carriers: a Protocol for Strategy, a thread for Adapter."""

import asyncio
import threading
from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING

from asyncio_patterns.domain import CarrierTimeoutError, Consignment, ConsignmentId
from asyncio_patterns.quoting import (
    AircoClient,
    AircoSource,
    FastlineSource,
    RateSource,
    cheapest,
    first_quote,
)

if TYPE_CHECKING:
    from conftest import AnswersAfter, FailsAfter, Runner, WaitingSource

    type WaitingSourceOf = Callable[[str, list[str], asyncio.Event], WaitingSource]
    type AnswersAfterOf = Callable[[str, asyncio.Event], AnswersAfter]
    type FailsAfterOf = Callable[[asyncio.Event], FailsAfter]

CONSIGNMENT = Consignment(ConsignmentId("CN-1"), "EU", Decimal("20"))


def test_the_cheapest_quote_wins_across_an_async_and_an_adapted_source(run: Runner) -> None:
    sources: list[RateSource] = [FastlineSource(), AircoSource(AircoClient())]

    quote = run(cheapest(CONSIGNMENT, sources))

    assert (quote.carrier, quote.total.amount) == ("AIRCO", Decimal("7.00"))


def test_the_adapter_runs_the_blocking_sdk_in_a_thread_while_the_loop_runs(run: Runner) -> None:
    ready = threading.Event()
    source = AircoSource(AircoClient(ready=ready))
    log: list[str] = []

    async def release() -> None:
        log.append("loop ran")
        ready.set()

    async def main() -> None:
        releasing = asyncio.create_task(release())
        quote = await source.quote(CONSIGNMENT)
        await releasing
        log.append(f"{quote.carrier} quoted")

    run(main())

    assert log == ["loop ran", "AIRCO quoted"]


def test_a_failing_carrier_cancels_the_other_quote(
    run: Runner, waiting_source: WaitingSourceOf, fails_after: FailsAfterOf
) -> None:
    started = asyncio.Event()
    log: list[str] = []
    sources: list[RateSource] = [waiting_source("AIRCO", log, started), fails_after(started)]

    async def main() -> list[str]:
        failures: list[str] = []
        try:
            await cheapest(CONSIGNMENT, sources)
        except* CarrierTimeoutError as group:
            failures.extend(str(error) for error in group.exceptions)
        return failures

    assert (run(main()), log) == (["FASTLINE did not answer"], ["AIRCO cancelled"])


def test_the_first_answer_cancels_the_rest_of_the_group(
    run: Runner, waiting_source: WaitingSourceOf, answers_after: AnswersAfterOf
) -> None:
    started = asyncio.Event()
    log: list[str] = []
    sources: list[RateSource] = [
        waiting_source("AIRCO", log, started),
        answers_after("FASTLINE", started),
    ]

    quote = run(first_quote(CONSIGNMENT, sources))

    assert (quote.carrier, log) == ("FASTLINE", ["AIRCO cancelled"])


def test_a_zero_timeout_cancels_a_quote_that_never_answers(
    run: Runner, waiting_source: WaitingSourceOf
) -> None:
    sources: list[RateSource] = [waiting_source("AIRCO", [], asyncio.Event())]

    async def main() -> bool:
        try:
            await cheapest(CONSIGNMENT, sources, within=0)
        except TimeoutError:  # the guard's own TimeoutError is not caught here
            return True
        return False

    assert run(main()) is True
