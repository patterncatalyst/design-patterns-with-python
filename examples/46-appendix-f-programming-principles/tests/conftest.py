"""Fixtures shared by the principle tests.

The suite runs under ``--import-mode=importlib``, so a test module cannot import this file by
name: values reach the tests as fixtures. The comparison form of the remittance reader, the one
that reaches through a shipment to its invoice, lives in this file. ``READERS`` is a
read-only mapping from a form's name to its function; the ``reader_form`` fixture runs a test once
per entry.
"""

from collections.abc import Callable, Mapping
from decimal import Decimal
from types import MappingProxyType

import pytest
from principles_reviewed.billing import Invoice, LineItem, Shipment, remittance_line
from principles_reviewed.domain import ConsignmentId, Money

type Reader = Callable[[Shipment], str]


def _chained_remittance(shipment: Shipment, /) -> str:
    # The comparison form: it reaches through the shipment to its invoice.
    return f"{shipment.consignment_id} {shipment.invoice.total}"


READERS: Mapping[str, Reader] = MappingProxyType(
    {"delegating": remittance_line, "chained": _chained_remittance}
)


@pytest.fixture(params=["delegating", "chained"])
def reader_form(request: pytest.FixtureRequest) -> Reader:
    return READERS[request.param]


@pytest.fixture
def credited() -> Shipment:
    """CN-3: freight 30.00 and duty 5.63 EUR, one credit of 10.63 EUR, so 25.00 EUR is due."""
    consignment_id = ConsignmentId("CN-3")
    invoice = Invoice(
        consignment_id,
        (
            LineItem("freight", Money(Decimal("30.00"))),
            LineItem("duty", Money(Decimal("5.63"))),
        ),
    )
    return Shipment(consignment_id, invoice, (LineItem("damaged pallet", Money(Decimal("10.63"))),))
