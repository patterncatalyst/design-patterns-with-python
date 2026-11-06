import threading
from dataclasses import FrozenInstanceError, dataclass, field, replace
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING

import pytest
from descriptors_properties.cargo import Consignment, Container

if TYPE_CHECKING:
    from conftest import ConsignmentFactory


def _stored(shipment: Consignment) -> bool:
    return "chargeable_kg" in vars(shipment)


def test_chargeable_weight_is_computed_on_first_access_and_stored(
    consignment: ConsignmentFactory,
) -> None:
    shipment = consignment(100)
    before = _stored(shipment)

    value = shipment.chargeable_kg

    assert (before, _stored(shipment), vars(shipment)["chargeable_kg"]) == (False, True, value)


@pytest.mark.parametrize(
    ("kilograms", "expected"),
    [(100, Decimal("160.32")), (250, Decimal(250))],
    ids=["bulky", "heavy"],
)
def test_chargeable_weight_is_the_larger_of_actual_and_volumetric_weight(
    consignment: ConsignmentFactory, kilograms: int, expected: Decimal
) -> None:
    assert consignment(kilograms).chargeable_kg == expected


@dataclass(frozen=True, slots=True)
class _SlottedLot:
    kilograms: Decimal

    @cached_property
    def doubled(self) -> Decimal:
        return self.kilograms * 2


def test_cached_property_needs_an_instance_dict() -> None:
    with pytest.raises(TypeError, match="No '__dict__' attribute"):
        _ = _SlottedLot(Decimal(1)).doubled


def test_a_frozen_dataclass_cannot_clear_a_cached_property(
    consignment: ConsignmentFactory,
) -> None:
    shipment = consignment(100)
    _ = shipment.chargeable_kg

    with pytest.raises(FrozenInstanceError, match="cannot delete field 'chargeable_kg'"):
        del shipment.chargeable_kg


def test_replace_recomputes_the_chargeable_weight(consignment: ConsignmentFactory) -> None:
    shipment = consignment(100)
    first = shipment.chargeable_kg

    heavier = replace(shipment, kilograms=Decimal(300))

    assert (first, heavier.chargeable_kg) == (Decimal("160.32"), Decimal(300))


class _CachingContainer(Container):
    """A container whose payload is cached, which is wrong for a load that changes."""

    @cached_property
    def payload_kg(self) -> Decimal:
        return super().payload_kg


def test_a_cached_property_over_mutable_state_goes_stale(
    consignment: ConsignmentFactory,
) -> None:
    cached = _CachingContainer("C-2", Decimal(2200), Decimal(28000))
    live = Container("C-3", Decimal(2200), Decimal(28000))
    # `load` itself reads the payload, so the cached form is filled with the cargo added by hand.
    cached.consignments.append(consignment(100))
    live.load(consignment(100))
    _ = cached.payload_kg
    cached.consignments.append(consignment(250))
    live.load(consignment(250))

    assert (cached.payload_kg, live.payload_kg) == (Decimal(100), Decimal(350))


@dataclass(frozen=True)
class _Lot:
    """A value whose getter waits for a second reader before it returns."""

    barrier: threading.Barrier
    runs: list[int] = field(default_factory=list, hash=False, compare=False)

    @cached_property
    def weight(self) -> int:
        self.barrier.wait()
        self.runs.append(1)
        return 2


def test_a_cached_property_getter_can_run_twice_under_threads() -> None:
    """Since 3.12 ``cached_property`` holds no lock, so two readers can both run the getter."""
    lot = _Lot(threading.Barrier(2, timeout=10))
    results: list[int] = []

    def read() -> None:
        results.append(lot.weight)

    threads = [threading.Thread(target=read) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    again = lot.weight

    assert (results, len(lot.runs), again, len(lot.runs)) == ([2, 2], 2, 2, 2)
