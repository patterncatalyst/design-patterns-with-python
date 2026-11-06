import threading
from contextlib import suppress
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from shortcut_patterns.declarations import CustomsError, declaration_from
from shortcut_patterns.documents import ConsignmentId
from shortcut_patterns.duties import DutyRateCache, duty_for

if TYPE_CHECKING:
    from conftest import CacheForm, DutyRateView, RecordingLoad, _HandoverRates

CODE = "0901.21"
OTHER = "6109.10"

# (stored rates, codes evicted first, code read twice, expected rate, expected loads)
CACHE_ROWS = [
    pytest.param({CODE: Decimal("6.5")}, [], CODE, Decimal("6.5"), [], id="hit"),
    pytest.param({}, [], OTHER, Decimal("8.0"), [OTHER], id="miss"),
    pytest.param({CODE: Decimal("6.5")}, [CODE], CODE, Decimal("8.0"), [CODE], id="evicted"),
]

_RECORD = {"consignment_id": "CN-1", "hs_code": CODE, "declared_value": "100.00"}


class _DutyBearingDeclaration:
    """A declaration whose ``duty`` property has a bug: it reads ``rate``, which is never set."""

    rate: Decimal

    @property
    def duty(self) -> Decimal:
        return Decimal(100) * self.rate


def _read_while_another_thread_evicts(cache: DutyRateView, rates: _HandoverRates) -> list[str]:
    """Read ``CODE`` in a thread that parks on its first read, and evict from this thread."""
    outcome: list[str] = []

    def read() -> None:
        try:
            outcome.append(str(cache.rate_for(CODE)))
        except KeyError as error:
            outcome.append(f"KeyError: {error}")

    reader = threading.Thread(target=read)
    reader.start()
    rates.barrier.wait()
    cache.evict(CODE)
    rates.barrier.wait()
    reader.join(timeout=30)
    assert not reader.is_alive()
    return outcome


@pytest.mark.parametrize(("stored", "evicted", "code", "rate", "loads"), CACHE_ROWS)
def test_every_cache_form_reads_loads_and_evicts_the_same_way(
    cache_form: CacheForm,
    recording_load: RecordingLoad,
    stored: dict[str, Decimal],
    evicted: list[str],
    code: str,
    rate: Decimal,
    loads: list[str],
) -> None:
    cache = cache_form(recording_load, dict(stored))
    for evicted_code in evicted:
        cache.evict(evicted_code)
    assert [cache.rate_for(code), cache.rate_for(code)] == [rate, rate]
    assert recording_load.codes == loads


def test_a_look_first_read_raises_when_another_thread_evicts_between_check_and_read(
    look_first_form: CacheForm, recording_load: RecordingLoad, handover_rates: _HandoverRates
) -> None:
    cache = look_first_form(recording_load, handover_rates)
    outcome = _read_while_another_thread_evicts(cache, handover_rates)
    assert (outcome, recording_load.codes) == (["KeyError: '0901.21'"], [])


def test_an_eafp_read_reloads_when_another_thread_evicts_first(
    eafp_form: CacheForm, recording_load: RecordingLoad, handover_rates: _HandoverRates
) -> None:
    cache = eafp_form(recording_load, handover_rates)
    outcome = _read_while_another_thread_evicts(cache, handover_rates)
    assert (outcome, recording_load.codes) == (["8.0"], [CODE])


def test_two_eafp_readers_that_both_miss_both_load() -> None:
    meeting = threading.Barrier(2, timeout=10)
    codes: list[str] = []

    def load(hs_code: str) -> Decimal:
        codes.append(hs_code)
        meeting.wait()
        return Decimal("8.0")

    cache = DutyRateCache(load)
    readers = [threading.Thread(target=cache.rate_for, args=(CODE,)) for _ in range(2)]
    for reader in readers:
        reader.start()
    for reader in readers:
        reader.join(timeout=30)
    assert [reader.is_alive() for reader in readers] == [False, False]
    assert codes == [CODE, CODE]


def test_evicting_an_absent_code_is_not_an_error(
    cache_form: CacheForm, recording_load: RecordingLoad
) -> None:
    cache = cache_form(recording_load, {})
    cache.evict(CODE)
    assert recording_load.codes == []


def test_declaration_from_reads_required_fields_and_an_optional_origin() -> None:
    bare = declaration_from(_RECORD)
    assert (bare.consignment_id, bare.hs_code, bare.declared_value) == (
        ConsignmentId("CN-1"),
        CODE,
        Decimal("100.00"),
    )
    assert bare.origin is None
    assert declaration_from({**_RECORD, "origin": "NL"}).origin == "NL"


@pytest.mark.parametrize("name", ["consignment_id", "hs_code", "declared_value"])
def test_a_missing_required_field_names_the_field(name: str) -> None:
    record = {key: value for key, value in _RECORD.items() if key != name}
    with pytest.raises(CustomsError, match=f"declaration is missing '{name}'") as info:
        declaration_from(record)
    assert info.value.__suppress_context__ is True


def test_getattr_with_a_default_hides_an_attribute_error_raised_inside_a_property() -> None:
    declaration = _DutyBearingDeclaration()
    assert getattr(declaration, "duty", Decimal(0)) == 0
    assert hasattr(declaration, "duty") is False
    with pytest.raises(AttributeError, match="has no attribute 'rate'"):
        declaration.duty  # noqa: B018


def test_suppress_skips_the_rest_of_its_block_after_the_first_exception() -> None:
    rates = {CODE: Decimal("6.5")}
    with suppress(KeyError):
        del rates["absent"]
        del rates[CODE]
    assert sorted(rates) == [CODE]


def test_duty_for_applies_the_cached_rate_to_the_declared_value(
    recording_load: RecordingLoad,
) -> None:
    declaration = declaration_from({**_RECORD, "declared_value": "100.00"})
    cache = DutyRateCache(recording_load, rates={CODE: Decimal("7.5")})
    assert str(duty_for(declaration, cache)) == "7.50"
    half_cent = declaration_from({**_RECORD, "declared_value": "0.10"})
    five_percent = DutyRateCache(recording_load, rates={CODE: Decimal("5")})
    assert str(duty_for(half_cent, five_percent)) == "0.01"
