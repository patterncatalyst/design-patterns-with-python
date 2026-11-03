"""PDP-012: ``functools.singledispatch`` over a hierarchy of cargo types."""

from dataclasses import dataclass
from functools import singledispatch, singledispatchmethod


@dataclass(frozen=True)
class Cargo:
    """Base of the cargo hierarchy."""

    reference: str


@dataclass(frozen=True)
class Pallet(Cargo):
    layers: int


@dataclass(frozen=True)
class Container(Cargo):
    teu: int


@dataclass(frozen=True)
class HazmatDrum(Cargo):
    un_number: str


@dataclass(frozen=True)
class Parcel(Cargo):
    grams: int


@singledispatch
def customs_label(cargo: Cargo) -> str:
    """Fallback: any cargo without a more specific registration."""
    return f"general cargo {cargo.reference}"


@customs_label.register
def _(cargo: Pallet) -> str:
    return f"pallet {cargo.reference} ({cargo.layers} layers)"


@customs_label.register
def _(cargo: Container) -> str:
    return f"container {cargo.reference} ({cargo.teu} TEU)"


@customs_label.register
def _(cargo: HazmatDrum) -> str:
    return f"HAZMAT {cargo.un_number} {cargo.reference}"


@singledispatch
def handling(cargo: Cargo) -> str:
    return "standard handling"


@handling.register
def _(cargo: Pallet | Parcel) -> str:
    """Union annotation: one function registered for several classes."""
    return "forklift or hand sort"


@handling.register
def _(cargo: HazmatDrum) -> str:
    return "segregate and placard"


class Labeller:
    """``singledispatchmethod`` dispatches on the first argument after ``self``."""

    prefix: str

    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    @singledispatchmethod
    def render(self, cargo: Cargo) -> str:
        return f"{self.prefix}: {cargo.reference}"

    @render.register
    def _(self, cargo: Container) -> str:
        return f"{self.prefix}: box {cargo.reference}"

    @render.register
    def _(self, cargo: Pallet | Parcel) -> str:
        return f"{self.prefix}: loose {cargo.reference}"


@dataclass(frozen=True)
class Truck:
    plate: str


@dataclass(frozen=True)
class Ship:
    name: str


type Vehicle = Truck | Ship


@singledispatch
def load_plan(cargo: Cargo, vehicle: Vehicle) -> str:
    """Dispatch on the first argument only; the second is matched inside each branch."""
    return f"{cargo.reference}: no plan for {type(cargo).__name__}"


@load_plan.register
def _(cargo: Container, vehicle: Vehicle) -> str:
    match vehicle:
        case Ship(name):
            return f"crane {cargo.reference} onto {name}"
        case Truck(plate):
            return f"chassis {cargo.reference} onto {plate}"


@load_plan.register
def _(cargo: Parcel, vehicle: Vehicle) -> str:
    match vehicle:
        case Truck():
            return f"hand-load {cargo.reference}"
        case Ship():
            return f"{cargo.reference}: parcels do not sail alone"
