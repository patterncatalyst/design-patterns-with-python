"""Fixtures shared by the reference tests.

The suite runs under ``--import-mode=importlib``, so a test module cannot import this file by
name: values reach the tests as fixtures, and the types below are imported under
``TYPE_CHECKING``. ``pytester`` is loaded by the test modules that use it, never here.
"""

from collections.abc import Callable
from decimal import Decimal
from typing import Protocol

import pytest
from pytest_reference.domain import Consignment, ConsignmentId, Weight


class MakeConsignment(Protocol):
    """Build a consignment; every argument has a default."""

    def __call__(
        self, consignment_id: str = "CN-1", /, *, zone: str = "EU", kilograms: str = "10"
    ) -> Consignment: ...


type NodeIds = Callable[[pytest.RunResult], list[str]]


@pytest.fixture
def consignment() -> Consignment:
    return Consignment(ConsignmentId("CN-1"), "EU", Weight(Decimal("10")))


@pytest.fixture
def make_consignment() -> MakeConsignment:
    """A factory fixture: the test decides how many consignments to build, and with what."""

    def make(
        consignment_id: str = "CN-1", /, *, zone: str = "EU", kilograms: str = "10"
    ) -> Consignment:
        return Consignment(ConsignmentId(consignment_id), zone, Weight(Decimal(kilograms)))

    return make


@pytest.fixture
def ran() -> list[str]:
    """Names of the fixtures that ran for the current test, in order."""
    return []


@pytest.fixture(autouse=True)
def note_autouse(ran: list[str]) -> None:
    """Applied to every test in the member without being named."""
    ran.append("autouse")


@pytest.fixture
def note_usefixtures(ran: list[str]) -> None:
    """Applied only where a test asks for it with ``usefixtures``."""
    ran.append("usefixtures")


@pytest.fixture
def rated(request: pytest.FixtureRequest) -> Consignment:
    """A ten-kilogram consignment in the zone given as the indirect parameter."""
    zone: str = request.param
    return Consignment(ConsignmentId("CN-9"), zone, Weight(Decimal("10")))


@pytest.fixture
def node_ids() -> NodeIds:
    """Read the node ids that ``--collect-only -q`` printed."""

    def read(result: pytest.RunResult) -> list[str]:
        return [line for line in result.outlines if "::" in line]

    return read
