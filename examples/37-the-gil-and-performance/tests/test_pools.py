"""The pools: same answers, different sharing."""

import pickle
from concurrent.futures import ProcessPoolExecutor
from decimal import Decimal

import pytest
from gil_and_performance.domain import Consignment, ConsignmentId
from gil_and_performance.pools import POOLS, append_reserved, rate_batch
from gil_and_performance.rating import quote

BATCH = tuple(
    Consignment(
        ConsignmentId(f"CN-{n}"), "EU" if n % 2 else "ASIA", Decimal(n * 7) + Decimal("0.3")
    )
    for n in range(1, 9)
)
GUARD_SECONDS = 10


@pytest.mark.parametrize("pool", ["thread", "process", "interpreter"])
def test_every_pool_rates_the_batch_as_the_serial_loop_does(pool: str) -> None:
    serial = [quote(consignment) for consignment in BATCH]

    assert rate_batch(BATCH, pool=POOLS[pool], workers=2) == serial


@pytest.mark.parametrize(
    ("pool", "caller_list"),
    [("thread", ["CN-1"]), ("process", []), ("interpreter", [])],
)
def test_threads_share_the_argument_and_processes_and_interpreters_copy_it(
    pool: str, caller_list: list[str]
) -> None:
    reserved: list[ConsignmentId] = []

    with POOLS[pool](1) as executor:
        returned = executor.submit(append_reserved, reserved, ConsignmentId("CN-1")).result(
            GUARD_SECONDS
        )

    assert (returned, reserved) == (1, caller_list)


def test_a_process_pool_cannot_send_a_lambda() -> None:
    with ProcessPoolExecutor(1) as executor:
        future = executor.submit(lambda: 1)

        with pytest.raises(pickle.PicklingError, match="Can't pickle"):
            future.result(GUARD_SECONDS)
