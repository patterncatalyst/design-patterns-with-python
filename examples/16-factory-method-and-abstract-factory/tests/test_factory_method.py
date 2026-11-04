import ast
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from decimal import Decimal
from pathlib import Path

import factories.factories
import pytest
from factories.carriers import (
    FASTLINE_LIVE,
    FASTLINE_SANDBOX,
    AircoGateway,
    CarrierGateway,
    FastlineGateway,
)
from factories.domain import CarrierSettings, ConsignmentId, Shipment, UnknownCarrierError
from factories.factories import GATEWAYS, make_gateway
from factories.kits import KITS, ship

CONSIGNMENT = ConsignmentId("CN-1")


class _BookingDesk(ABC):
    """The GoF shape, kept as a comparison: a creator whose subclasses choose the gateway."""

    @abstractmethod
    def create_gateway(self, settings: CarrierSettings) -> CarrierGateway[str]: ...

    def book(self, consignment_id: ConsignmentId, settings: CarrierSettings) -> str:
        return self.create_gateway(settings).book(consignment_id)


class _FastlineDesk(_BookingDesk):
    def create_gateway(self, settings: CarrierSettings) -> CarrierGateway[str]:
        return FastlineGateway.from_settings(settings)


class _AircoDesk(_BookingDesk):
    def create_gateway(self, settings: CarrierSettings) -> CarrierGateway[str]:
        return AircoGateway.from_settings(settings)


_DESKS: Mapping[str, _BookingDesk] = frozendict(
    {"FASTLINE": _FastlineDesk(), "AIRCO": _AircoDesk()}
)


def _by_registry(code: str, settings: CarrierSettings) -> str:
    return make_gateway(code, settings).book(CONSIGNMENT)


def _by_creator(code: str, settings: CarrierSettings) -> str:
    return _DESKS[code].book(CONSIGNMENT, settings)


@pytest.mark.parametrize("book", [_by_registry, _by_creator], ids=["registry", "creator"])
def test_a_registered_constructor_builds_each_carrier_gateway(
    book: Callable[[str, CarrierSettings], str],
    carrier: str,
    settings: CarrierSettings,
    expected: Shipment,
) -> None:
    assert book(carrier, settings) == expected.reference


def test_a_classmethod_constructor_returns_the_subclass_it_is_called_on(
    settings: CarrierSettings,
) -> None:
    class SandboxFastlineGateway(FastlineGateway):
        pass

    class SandboxAircoGateway(AircoGateway):
        pass

    fastline = SandboxFastlineGateway.from_settings(settings)
    airco = SandboxAircoGateway.from_settings(settings)

    assert type(fastline) is SandboxFastlineGateway
    assert type(airco) is SandboxAircoGateway
    assert airco.account == "ACC-7"


def test_a_sandbox_setting_selects_the_sandbox_endpoint() -> None:
    live = FastlineGateway.from_settings(CarrierSettings(account="ACC-7"))
    sandbox = FastlineGateway.from_settings(CarrierSettings(account="ACC-7", sandbox=True))

    assert live.endpoint == FASTLINE_LIVE
    assert sandbox.endpoint == FASTLINE_SANDBOX


def _unknown_by_gateways(settings: CarrierSettings) -> object:
    return make_gateway("NOSUCH", settings)


def _unknown_by_kits(settings: CarrierSettings) -> object:
    return ship("NOSUCH", CONSIGNMENT, Decimal(10), settings)


@pytest.mark.parametrize(
    "lookup", [_unknown_by_gateways, _unknown_by_kits], ids=["gateways", "kits"]
)
def test_an_unknown_carrier_code_is_an_unknown_carrier_error(
    lookup: Callable[[CarrierSettings], object], settings: CarrierSettings
) -> None:
    with pytest.raises(UnknownCarrierError, match="unknown carrier 'NOSUCH'") as raised:
        lookup(settings)

    assert raised.value.__cause__ is None
    assert raised.value.__suppress_context__


@pytest.mark.parametrize("registry", [GATEWAYS, KITS], ids=["gateways", "kits"])
def test_the_carrier_registries_are_read_only(registry: Mapping[str, object]) -> None:
    with pytest.raises(TypeError, match="does not support item assignment"):
        registry["NOSUCH"] = 1  # type: ignore[index]

    assert not isinstance(registry, dict)


def _class_names(source: str) -> set[str]:
    return {node.name for node in ast.walk(ast.parse(source)) if isinstance(node, ast.ClassDef)}


def test_the_creator_design_declares_three_classes_where_the_registry_declares_none() -> None:
    registry_source = Path(factories.factories.__file__).read_text()
    creators = {
        node.name
        for node in ast.walk(ast.parse(Path(__file__).read_text()))
        if isinstance(node, ast.ClassDef)
        and (
            node.name == "_BookingDesk"
            or any(isinstance(base, ast.Name) and base.id == "_BookingDesk" for base in node.bases)
        )
    }

    assert _class_names(registry_source) == set()
    assert creators == {"_AircoDesk", "_BookingDesk", "_FastlineDesk"}


def test_a_type_registry_accepts_a_class_that_cannot_be_called_without_arguments(
    settings: CarrierSettings,
) -> None:
    by_type: Mapping[str, type[CarrierGateway[str]]] = {
        "FASTLINE": FastlineGateway,
        "AIRCO": AircoGateway,
    }

    assert by_type["FASTLINE"]() == FastlineGateway()
    with pytest.raises(TypeError, match="missing 1 required positional argument: 'account'"):
        by_type["AIRCO"]()
