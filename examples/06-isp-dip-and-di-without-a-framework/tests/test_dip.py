import ast
import inspect
import os
import re
from pathlib import Path
from types import ModuleType

import mypy.api
import pytest
from isp_dip_di import booking, carriers, tracking
from isp_dip_di.booking import BookingGateway, BookingService
from isp_dip_di.domain import BookingRequest
from isp_dip_di.tracking import TrackingGateway
from pytest_mock import MockerFixture

_SRC = Path(__file__).resolve().parents[1] / "src"


class FakeBooker:
    """A fake that implements only what booking consumes, and records what it was asked."""

    def __init__(self) -> None:
        self.requests: list[BookingRequest] = []

    def book(self, request: BookingRequest, /) -> str:
        self.requests.append(request)
        return "FAKE:1"

    def cancel(self, reference: str, /) -> None:
        return None


def imported_modules(module: ModuleType) -> set[str]:
    """Every absolute module name the source imports, with relative imports resolved."""
    package = module.__package__ or ""
    names: set[str] = set()
    for node in ast.walk(ast.parse(inspect.getsource(module))):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                parts = package.split(".")[: len(package.split(".")) - node.level + 1]
                base = ".".join([*parts, *([node.module] if node.module else [])])
            names.add(base)
            names.update(f"{base}.{alias.name}" for alias in node.names)
    return names


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
    return set(re.findall(r"\[([a-z-]+)\]", stdout))


def test_booking_service_runs_against_an_injected_fake(
    request_for: BookingRequest, records: list[str]
) -> None:
    fake = FakeBooker()
    service = BookingService(fake, records.append)

    reference = service.book(request_for)

    assert reference == "FAKE:1"
    assert fake.requests == [request_for]
    assert records == ["booked FAKE:1"]


@pytest.mark.parametrize("policy", [booking, tracking], ids=["booking", "tracking"])
def test_policy_modules_do_not_import_the_adapters(policy: ModuleType) -> None:
    imports = imported_modules(policy)

    assert imports  # the collector found the module's own imports
    assert "isp_dip_di.domain" in imports
    assert not imports & {"isp_dip_di.carriers", "isp_dip_di.app"}


def test_adapters_import_neither_policy_nor_protocols() -> None:
    imports = imported_modules(carriers)

    assert "isp_dip_di.domain" in imports
    assert not imports & {"isp_dip_di.booking", "isp_dip_di.tracking", "isp_dip_di.app"}


_AUTOSPEC_OF_THE_WRONG_PROTOCOL = """
from isp_dip_di.booking import BookingService
from isp_dip_di.tracking import TrackingGateway
from pytest_mock import MockerFixture


def build(mocker: MockerFixture) -> BookingService:
    gateway = mocker.create_autospec(TrackingGateway, instance=True)
    return BookingService(gateway=gateway, audit=lambda message: None)
"""


def test_autospec_bypasses_mypy(tmp_path: Path) -> None:
    stdout, status = _run(_AUTOSPEC_OF_THE_WRONG_PROTOCOL, tmp_path)

    assert status == 0
    assert stdout == ""


def test_autospec_enforces_the_protocol_shape_at_runtime(
    mocker: MockerFixture, records: list[str]
) -> None:
    wrong = mocker.create_autospec(TrackingGateway, instance=True)
    service = BookingService(gateway=wrong, audit=records.append)

    with pytest.raises(AttributeError):
        service.cancel("FASTLINE:CN-1")
    with pytest.raises(TypeError, match="missing a required argument"):
        wrong.track()

    right = mocker.create_autospec(BookingGateway, instance=True)
    service = BookingService(gateway=right, audit=records.append)

    service.cancel("FASTLINE:CN-1")

    right.cancel.assert_called_once_with("FASTLINE:CN-1")
    assert records == ["cancelled FASTLINE:CN-1"]


_HEADER = """
from functools import partial

from isp_dip_di.domain import ConsignmentId
from isp_dip_di.tracking import TrackingGateway, tracking_history
"""

_BIND_A_NON_GATEWAY = (
    _HEADER
    + """

bound = partial(tracking_history, gateway=42)
"""
)

_CALL_WITH_AN_INT = (
    _HEADER
    + """

def use(gateway: TrackingGateway) -> None:
    bound = partial(tracking_history, gateway=gateway)
    bound(42)
"""
)

_ASSIGN_TO_A_MISMATCHED_CALLABLE = (
    _HEADER
    + """
from collections.abc import Callable

from isp_dip_di.domain import TrackingHistory


def use(gateway: TrackingGateway) -> None:
    wrong: Callable[[int], TrackingHistory] = partial(tracking_history, gateway=gateway)
    wrong(1)
"""
)


@pytest.mark.parametrize(
    ("snippet", "status", "codes"),
    [
        (_BIND_A_NON_GATEWAY, 1, {"arg-type"}),
        (_CALL_WITH_AN_INT, 1, {"arg-type"}),
        (_ASSIGN_TO_A_MISMATCHED_CALLABLE, 0, set()),
    ],
    ids=["binding", "call", "assignment"],
)
def test_mypy_checks_a_partial_at_binding_and_call_but_not_at_assignment(
    snippet: str, status: int, codes: set[str], tmp_path: Path
) -> None:
    stdout, actual_status = _run(snippet, tmp_path)

    assert actual_status == status
    assert _codes(stdout) == codes
    if status == 0:
        assert stdout == ""
