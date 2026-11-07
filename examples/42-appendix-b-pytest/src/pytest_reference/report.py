"""Writing quotes as lines of text."""

import sys
from collections.abc import Mapping
from decimal import Decimal
from typing import TextIO

from pytest_reference.domain import ConsignmentId


def write_quotes(quotes: Mapping[ConsignmentId, Decimal], /, *, out: TextIO | None = None) -> None:
    """Write one ``id total`` line per consignment, to ``out`` or to the current ``sys.stdout``."""
    stream = sys.stdout if out is None else out
    for consignment_id, total in quotes.items():
        stream.write(f"{consignment_id} {total}\n")
