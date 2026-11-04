import os
import re
from pathlib import Path

import mypy.api
import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"


def _run(snippet: str, tmp_path: Path) -> tuple[str, int]:
    """Type-check a snippet strictly, finding the package through the member's src directory."""
    config = tmp_path / "mypy.ini"
    config.write_text(f"[mypy]\nmypy_path = {_SRC}\n")
    stdout, _stderr, status = mypy.api.run(
        [
            "--strict",
            "--config-file",
            str(config),
            "--cache-dir",
            os.devnull,
            "--no-error-summary",
            "-c",
            snippet,
        ]
    )
    return stdout, status


def _codes(stdout: str) -> set[str]:
    return set(re.findall(r"\[([a-z-]+)\]$", stdout, re.MULTILINE))


_CALLABLE_SLOT = """
from collections.abc import Callable, Mapping

from factories.carriers import AircoGateway, CarrierGateway, FastlineGateway

SLOTS: Mapping[str, Callable[[], CarrierGateway[str]]] = {
    "FASTLINE": FastlineGateway,
    "AIRCO": AircoGateway,
}
"""

_TYPE_SLOT = """
from collections.abc import Mapping

from factories.carriers import AircoGateway, CarrierGateway, FastlineGateway

BY_TYPE: Mapping[str, type[CarrierGateway[str]]] = {
    "FASTLINE": FastlineGateway,
    "AIRCO": AircoGateway,
}
gateway = BY_TYPE["AIRCO"]()
"""

_PARTIAL_IN_TYPE_SLOT = """
from collections.abc import Mapping
from functools import partial

from factories.carriers import AircoGateway, CarrierGateway

BY_TYPE: Mapping[str, type[CarrierGateway[str]]] = {"AIRCO": partial(AircoGateway, "ACC-1")}
"""

_PROTOCOL_IN_TYPE_SLOT = """
from collections.abc import Mapping

from factories.carriers import CarrierGateway

BY_TYPE: Mapping[str, type[CarrierGateway[str]]] = {"ANY": CarrierGateway}
"""


@pytest.mark.parametrize(
    ("snippet", "status", "codes", "fragment"),
    [
        (_CALLABLE_SLOT, 1, {"dict-item"}, '"type[AircoGateway]"'),
        (_TYPE_SLOT, 0, set(), ""),
        (_PARTIAL_IN_TYPE_SLOT, 1, {"dict-item"}, '"partial[AircoGateway]"'),
        (_PROTOCOL_IN_TYPE_SLOT, 1, {"type-abstract"}, "Only concrete class can be given"),
    ],
    ids=["callable-slot", "type-slot", "partial-in-type-slot", "protocol-in-type-slot"],
)
def test_mypy_checks_a_constructor_slot_but_not_a_type_slot(
    snippet: str, status: int, codes: set[str], fragment: str, tmp_path: Path
) -> None:
    stdout, actual = _run(snippet, tmp_path)

    assert actual == status
    assert _codes(stdout) == codes
    assert fragment in stdout


_CLASSMETHOD_WITH_ANOTHER_SIGNATURE = """
from collections.abc import Mapping
from typing import Self

from factories.carriers import AircoGateway
from factories.factories import GatewayFactory


class EnvAircoGateway(AircoGateway):
    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> Self:
        return cls(env["AIRCO_ACCOUNT"])


BY_ENV: Mapping[str, GatewayFactory] = {"AIRCO": EnvAircoGateway.from_env}
"""


def test_mypy_checks_a_classmethod_constructor_against_the_slot(tmp_path: Path) -> None:
    stdout, status = _run(_CLASSMETHOD_WITH_ANOTHER_SIGNATURE, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"dict-item"}
    assert 'expected "str": "Callable[[CarrierSettings], CarrierGateway[str]]"' in stdout


# Reduced models: self-contained functions that stand for the if-chains in test_if_chains.py.
_STR_CODE = """
def make(code: str) -> int:
    if code == "FASTLINE":
        return 1
    if code == "AIRCO":
        return 2
    raise LookupError(code)
"""

_LITERAL_CODE = """
from typing import Literal, assert_never

type CarrierCode = Literal["FASTLINE", "AIRCO"]


def make(code: CarrierCode) -> int:
    match code:
        case "FASTLINE":
            return 1
        case _:
            assert_never(code)
"""


@pytest.mark.parametrize(
    ("snippet", "status", "codes", "fragment"),
    [
        (_STR_CODE, 0, set(), ""),
        (_LITERAL_CODE, 1, {"arg-type"}, "Literal['AIRCO']"),
    ],
    ids=["str-code", "literal-code"],
)
def test_mypy_cannot_see_a_carrier_missing_from_an_if_chain(
    snippet: str, status: int, codes: set[str], fragment: str, tmp_path: Path
) -> None:
    stdout, actual = _run(snippet, tmp_path)

    assert actual == status
    assert _codes(stdout) == codes
    assert fragment in stdout


_MIXED_REFERENCE_TYPES = """
from factories.carriers import AircoLabelPrinter, FastlineGateway, FastlineRates
from factories.kits import CarrierKit

kit = CarrierKit(
    gateway=FastlineGateway.from_settings,
    label_printer=AircoLabelPrinter,
    rates=FastlineRates,
)
"""


def test_mypy_rejects_a_kit_that_mixes_reference_types(tmp_path: Path) -> None:
    stdout, status = _run(_MIXED_REFERENCE_TYPES, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"misc"}
    assert 'Cannot infer value of type parameter "R" of "CarrierKit"' in stdout


_MIXED_RATES = """
from factories.carriers import AircoRates, FastlineGateway, FastlineLabelPrinter
from factories.kits import CarrierKit

kit = CarrierKit(
    gateway=FastlineGateway.from_settings,
    label_printer=FastlineLabelPrinter,
    rates=AircoRates,
)
"""

_PLAIN_PRINTER = """
from dataclasses import dataclass

from factories.carriers import AircoGateway, AircoRates
from factories.kits import CarrierKit


@dataclass(frozen=True, slots=True)
class PlainLabelPrinter:
    def label(self, reference: str, /) -> str:
        return reference


kit = CarrierKit(
    gateway=AircoGateway.from_settings,
    label_printer=PlainLabelPrinter,
    rates=AircoRates,
)
"""


@pytest.mark.parametrize(
    "snippet", [_MIXED_RATES, _PLAIN_PRINTER], ids=["mixed-rates", "plain-printer"]
)
def test_mypy_accepts_kits_that_mix_untied_products(snippet: str, tmp_path: Path) -> None:
    stdout, status = _run(snippet, tmp_path)

    assert status == 0
    assert stdout == ""


_REGISTRY_TYPED_BY_ONE_FAMILY = """
from collections.abc import Mapping

from factories.kits import FASTLINE_KIT, CarrierKit

KITS: Mapping[str, CarrierKit[str]] = {"FASTLINE": FASTLINE_KIT}
"""


def test_mypy_rejects_a_kit_registry_typed_by_one_family(tmp_path: Path) -> None:
    stdout, status = _run(_REGISTRY_TYPED_BY_ONE_FAMILY, tmp_path)

    assert status == 1
    assert _codes(stdout) == {"dict-item"}
    assert '"CarrierKit[FastlineReference]"; expected "str": "CarrierKit[str]"' in stdout
