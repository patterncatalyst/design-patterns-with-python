"""Fixtures. The comparison forms, the GoF component classes and a `functools.cache` pool, live
here as fixture parameters so that they run the same tables as the forms in the model code."""

import functools
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from decimal import Decimal

import pytest
from composite_flyweight.domain import (
    Commodity,
    Consignment,
    ConsignmentId,
    ConsolidatedShipment,
    Weight,
)
from composite_flyweight.flyweights import CATALOGUE, CommodityPool, UnknownCommodityError

LITHIUM = "850760"
COFFEE = "090111"


@pytest.fixture
def pool() -> CommodityPool:
    return CommodityPool()


@pytest.fixture
def make_consignment(pool: CommodityPool) -> Callable[..., Consignment]:
    """Build a consignment from an id, a weight in kilograms and an HS code."""

    def make(consignment_id: str, kilograms: str, hs_code: str = COFFEE) -> Consignment:
        return Consignment(
            id=ConsignmentId(consignment_id),
            weight=Weight(Decimal(kilograms)),
            commodity=pool.get(hs_code),
            origin="NLRTM",
            destination="SGSIN",
        )

    return make


@pytest.fixture
def nested(make_consignment: Callable[..., Consignment]) -> ConsolidatedShipment:
    """CN-1 (10 kg), a nested group of CN-3 (2.5 kg) and CN-4 (4 kg), then CN-2 (7.25 kg).

    CN-4 is dangerous goods. The total is 23.75 kg. The consignments directly beneath the
    top group weigh 17.25 kg.
    """
    inner = ConsolidatedShipment(
        "CS-INNER",
        (make_consignment("CN-3", "2.5"), make_consignment("CN-4", "4", LITHIUM)),
    )
    return ConsolidatedShipment(
        "CS-1",
        (make_consignment("CN-1", "10"), inner, make_consignment("CN-2", "7.25")),
    )


@pytest.fixture
def flat_weight() -> Callable[[ConsolidatedShipment], Decimal]:
    """Comparison: a total that sums the consignments directly beneath a group and stops there."""

    def total(group: ConsolidatedShipment) -> Decimal:
        return sum(
            (p.weight.kilograms for p in group.parts if isinstance(p, Consignment)),
            start=Decimal(0),
        )

    return total


# Comparison: the GoF form, a base class that declares the child operations for every component.
# A leaf inherits `add` and refuses it only when the program runs.
class _Component(ABC):
    @abstractmethod
    def weight(self) -> Decimal: ...

    def add(self, component: _Component, /) -> None:
        raise TypeError(f"{type(self).__name__} cannot hold components")


class _ComponentLeaf(_Component):
    def __init__(self, kilograms: Decimal) -> None:
        self._kilograms = kilograms

    def weight(self) -> Decimal:
        return self._kilograms


class _ComponentGroup(_Component):
    def __init__(self) -> None:
        self._children: list[_Component] = []

    def add(self, component: _Component, /) -> None:
        self._children.append(component)

    def weight(self) -> Decimal:
        return sum((child.weight() for child in self._children), start=Decimal(0))


def _component_tree(nested: ConsolidatedShipment) -> _ComponentGroup:
    """The same structure as `nested`, in the mutable component form."""
    group = _ComponentGroup()
    for part in nested.parts:
        if isinstance(part, Consignment):
            group.add(_ComponentLeaf(part.weight.kilograms))
        else:
            group.add(_component_tree(part))
    return group


@pytest.fixture
def add_to_a_component_leaf() -> Callable[[], None]:
    """Attach one component to a leaf: the call the base class declares for every component."""

    def attach() -> None:
        _ComponentLeaf(Decimal(5)).add(_ComponentLeaf(Decimal(1)))

    return attach


@pytest.fixture
def self_containing_weight() -> Callable[[], Decimal]:
    """The weight of a group that has been added to itself. The `add` itself succeeds."""
    group = _ComponentGroup()
    group.add(group)
    return group.weight


@pytest.fixture(params=["frozen-union", "component-classes"])
def tree_form(
    request: pytest.FixtureRequest, nested: ConsolidatedShipment
) -> Callable[[], Decimal]:
    """The total kilograms of the `nested` structure, built in the parametrised form."""
    if request.param == "frozen-union":
        return lambda: nested.weight.kilograms
    return _component_tree(nested).weight


@pytest.fixture
def cached_pool() -> Callable[[str], Commodity]:
    """Comparison: `functools.cache` over a fresh builder, so nothing outlives the test."""

    def build(hs_code: str, /) -> Commodity:
        try:
            description, dangerous_goods = CATALOGUE[hs_code]
        except KeyError:
            raise UnknownCommodityError(f"unknown commodity {hs_code!r}") from None
        return Commodity(hs_code, description, dangerous_goods)

    return functools.cache(build)


@pytest.fixture(params=["weak-pool", "cache"])
def pool_form(
    request: pytest.FixtureRequest, pool: CommodityPool, cached_pool: Callable[[str], Commodity]
) -> Callable[[str], Commodity]:
    """Get a commodity by code from the parametrised form."""
    if request.param == "weak-pool":
        return pool.get
    return cached_pool


@pytest.fixture
def recursion_limit() -> Iterator[None]:
    """Pin the limit at CPython's default of 1000 and restore it afterwards.

    `mypy.api.run` raises the limit for the whole process, so without this a test that expects a
    `RecursionError` would depend on whether a static test ran before it.
    """
    previous = sys.getrecursionlimit()
    sys.setrecursionlimit(1000)
    try:
        yield
    finally:
        sys.setrecursionlimit(previous)
