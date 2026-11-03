import dis
import functools

import pytest
from feature_spikes.concurrency import (
    LoadCounter,
    LockedCounter,
    LockedLazyValue,
    RacyLazyValue,
    UnsafeCounter,
    alternating_pollers,
    gather_in_threads,
    hammer,
    lost_update_with_barrier,
    rendezvous_loader,
)


def test_increment_is_several_bytecodes_not_one_operation() -> None:
    ops = [i.opname for i in dis.get_instructions(UnsafeCounter.bump)]
    assert ops.index("LOAD_ATTR") < ops.index("BINARY_OP") < ops.index("STORE_ATTR")


def test_forced_gap_loses_an_update_every_time() -> None:
    assert lost_update_with_barrier() == 1  # two increments, one survives


def test_lock_makes_the_read_modify_write_correct() -> None:
    assert hammer(LockedCounter(), workers=4, rounds=2_000) == 8_000


def test_unsafe_counter_never_exceeds_the_true_total() -> None:
    # Only the upper bound is deterministic: losses are possible, gains are not.
    assert hammer(UnsafeCounter(), workers=4, rounds=2_000) <= 8_000


def test_pollers_interleave_in_handshake_order() -> None:
    log = alternating_pollers(["a1", "a2", "a3"], ["b1", "b2", "b3"])
    assert log == ["a1", "b1", "a2", "b2", "a3", "b3"]


def test_pollers_reject_uneven_feeds() -> None:
    with pytest.raises(ValueError, match="same number"):
        alternating_pollers(["a1"], [])


def test_check_then_set_runs_the_loader_twice() -> None:
    loads = LoadCounter(rendezvous_loader(2, "rates"))
    cache = RacyLazyValue(loads)
    assert gather_in_threads(cache.get, workers=2) == ["rates", "rates"]
    assert loads.calls == 2


def test_functools_cache_does_not_make_the_loader_run_once() -> None:
    loads = LoadCounter(rendezvous_loader(2, "rates"))
    cached = functools.cache(loads)
    assert gather_in_threads(cached, workers=2) == ["rates", "rates"]
    assert loads.calls == 2


def test_double_checked_lock_runs_the_loader_once() -> None:
    loads = LoadCounter(lambda: "rates")
    cache = LockedLazyValue(loads)
    assert gather_in_threads(cache.get, workers=8) == ["rates"] * 8
    assert loads.calls == 1
