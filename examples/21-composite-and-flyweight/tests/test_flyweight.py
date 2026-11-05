import dataclasses
import gc
import weakref
from collections.abc import Callable

import pytest
from composite_flyweight.domain import Commodity
from composite_flyweight.flyweights import (
    CATALOGUE,
    CommodityPool,
    PortCodeError,
    UnknownCommodityError,
    port_code,
    route,
)

LITHIUM = "850760"
COFFEE = "090111"


def test_the_pool_returns_one_commodity_per_code(pool_form: Callable[[str], Commodity]) -> None:
    assert pool_form(LITHIUM) is pool_form(LITHIUM)
    assert pool_form(LITHIUM) is not pool_form(COFFEE)
    assert pool_form(LITHIUM).description == "lithium-ion batteries"


def test_an_unknown_commodity_code_is_refused(pool_form: Callable[[str], Commodity]) -> None:
    with pytest.raises(UnknownCommodityError, match="unknown commodity '999999'") as refused:
        pool_form("999999")

    assert refused.value.__suppress_context__  # the lookup's KeyError is not shown as the cause


def test_the_weak_pool_drops_a_commodity_nobody_holds(pool: CommodityPool) -> None:
    first = pool.get(LITHIUM)
    first_ref = weakref.ref(first)
    assert len(pool) == 1

    del first
    # CPython usually frees an object at its last reference, but the language promises no
    # immediate finalisation, so collect explicitly before asserting.
    gc.collect()

    assert first_ref() is None
    assert len(pool) == 0
    second = pool.get(LITHIUM)
    assert second == Commodity(LITHIUM, "lithium-ion batteries", True)
    assert len(pool) == 1


def test_a_cache_keeps_every_commodity_it_has_made(
    cached_pool: Callable[[str], Commodity],
) -> None:
    first_ref = weakref.ref(cached_pool(LITHIUM))

    gc.collect()  # the cache, not luck, is what keeps it: nothing else holds the commodity

    kept = first_ref()
    assert kept is not None
    assert cached_pool(LITHIUM) is kept


def test_a_pool_needs_commodities_that_accept_weak_references() -> None:
    @dataclasses.dataclass(frozen=True, slots=True)
    class Plain:
        hs_code: str

    pool: weakref.WeakValueDictionary[str, Plain] = weakref.WeakValueDictionary()

    with pytest.raises(TypeError, match="cannot create weak reference"):
        pool["850760"] = Plain("850760")


def test_equal_commodities_need_not_be_the_same_object() -> None:
    first = Commodity(LITHIUM, "lithium-ion batteries", True)
    second = Commodity(LITHIUM, "lithium-ion batteries", True)

    assert first == second
    assert hash(first) == hash(second)
    assert first is not second
    assert len({first, second}) == 1


def test_a_shared_mutable_commodity_changes_every_consignment() -> None:
    @dataclasses.dataclass
    class MutableCommodity:
        hs_code: str
        dangerous_goods: bool

    shared = MutableCommodity(LITHIUM, True)
    first_line = ("CN-1", shared)
    second_line = ("CN-2", shared)

    first_line[1].dangerous_goods = False

    assert second_line[1].dangerous_goods is False
    frozen = Commodity(LITHIUM, "lithium-ion batteries", True)
    with pytest.raises(dataclasses.FrozenInstanceError):
        frozen.dangerous_goods = False  # type: ignore[misc]


def test_commodities_have_no_instance_dict() -> None:
    commodity = Commodity(LITHIUM, "lithium-ion batteries", True)

    assert not hasattr(commodity, "__dict__")
    assert "__weakref__" in Commodity.__slots__


def test_split_port_codes_are_equal_but_distinct_objects() -> None:
    """Observed on CPython 3.15.2: ``split`` builds a new string for each piece."""
    line = ";".join(["NLRTM", "SGSIN", "NLRTM"])  # built at run time, so not a shared literal
    first, _second, third = line.split(";")

    assert first == third
    assert first is not third


def test_interned_port_codes_are_one_object() -> None:
    calls = route("NLRTM;SGSIN;NLRTM")

    assert calls[0].port == calls[2].port == "NLRTM"
    assert calls[0].port is calls[2].port
    assert [call.sequence for call in calls] == [1, 2, 3]


@pytest.mark.parametrize("text", ["nlrtm", "NLR"], ids=["lowercase", "too-short"])
def test_a_malformed_port_code_is_refused(text: str) -> None:
    with pytest.raises(PortCodeError, match="malformed port code"):
        port_code(text)


def test_the_commodity_catalogue_is_read_only() -> None:
    with pytest.raises(TypeError, match="does not support item assignment"):
        CATALOGUE["123456"] = ("tea", False)  # type: ignore[index]

    assert "123456" not in CATALOGUE
