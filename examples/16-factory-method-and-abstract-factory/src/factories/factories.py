"""Factory Method as a registry of constructors in a Callable slot."""

from collections.abc import Callable, Mapping

from factories.carriers import AircoGateway, CarrierGateway, FastlineGateway
from factories.domain import CarrierSettings, UnknownCarrierError

type GatewayFactory = Callable[[CarrierSettings], CarrierGateway[str]]

GATEWAYS: Mapping[str, GatewayFactory] = frozendict(
    {
        "FASTLINE": FastlineGateway.from_settings,
        "AIRCO": AircoGateway.from_settings,
    }
)


def make_gateway(code: str, settings: CarrierSettings) -> CarrierGateway[str]:
    try:
        factory = GATEWAYS[code]
    except KeyError:
        raise UnknownCarrierError(f"unknown carrier {code!r}") from None
    return factory(settings)
