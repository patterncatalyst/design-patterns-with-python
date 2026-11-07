"""Rating a batch through thread, process and interpreter pools.

The worker functions live in this package, not in a test module, because a process or
interpreter worker must import them by name.
"""

from collections.abc import Callable, Iterable
from concurrent.futures import (
    Executor,
    InterpreterPoolExecutor,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)

from gil_and_performance.domain import Consignment, ConsignmentId, RateQuote
from gil_and_performance.rating import quote

# A class cannot stand in here: mypy rejects calling type[Executor] with max_workers.
type PoolFactory = Callable[[int], Executor]

POOLS: frozendict[str, PoolFactory] = frozendict(
    thread=ThreadPoolExecutor,
    process=ProcessPoolExecutor,
    interpreter=InterpreterPoolExecutor,
)


def rate_batch(
    batch: Iterable[Consignment], /, *, pool: PoolFactory, workers: int = 4
) -> list[RateQuote]:
    """Rate every consignment in the pool, in batch order."""
    with pool(workers) as executor:
        return list(executor.map(quote, batch))


def append_reserved(reserved: list[ConsignmentId], consignment_id: ConsignmentId) -> int:
    """Record a reservation in the list it is given: the witness for what a pool shares.

    A thread pool appends to the caller's list. A process or interpreter pool appends to a copy.
    """
    reserved.append(consignment_id)
    return len(reserved)
