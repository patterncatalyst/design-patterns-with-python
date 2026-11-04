import sys
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

import pytest
from testing_baseline.carriers import CarrierQuote, CarrierTimeoutError
from testing_baseline.domain import Consignment, ConsignmentId, Money, Weight


class FakeGateway:
    """A hand-written gateway: checked by mypy, records what it was asked to book."""

    def __init__(self, carrier: str, amount: Money, *, times_out: bool = False) -> None:
        self.carrier = carrier
        self.amount = amount
        self.times_out = times_out
        self.booked: list[Consignment] = []

    def quote(self, consignment: Consignment, /) -> CarrierQuote:
        if self.times_out:
            raise CarrierTimeoutError(self.carrier)
        return CarrierQuote(self.carrier, self.amount)

    def book(self, consignment: Consignment, /) -> str:
        self.booked.append(consignment)
        return f"{self.carrier.upper()}:{consignment.id}"


class FakeFactory(Protocol):
    def __call__(self, carrier: str, amount: Money, *, times_out: bool = False) -> FakeGateway: ...


@pytest.fixture
def consignment() -> Consignment:
    return Consignment(id=ConsignmentId("CN-00000001"), weight=Weight(100.0), destination="SGSIN")


@pytest.fixture
def fixed_now() -> datetime:
    return datetime(2026, 11, 4, 9, 0, tzinfo=UTC)


@pytest.fixture
def make_fake() -> FakeFactory:
    def make(carrier: str, amount: Money, *, times_out: bool = False) -> FakeGateway:
        return FakeGateway(carrier, amount, times_out=times_out)

    return make


@pytest.fixture
def quote_log(tmp_path: Path) -> Iterator[Path]:
    """A log file for the test; the teardown line is written whether the test passes or fails."""
    log = tmp_path / "quotes.log"
    log.write_text("setup\n", encoding="utf-8")
    yield log
    with log.open("a", encoding="utf-8") as handle:
        handle.write("teardown\n")
    sys.stdout.write(f"quote_log teardown: {log.name}\n")
