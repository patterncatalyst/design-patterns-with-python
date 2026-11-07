---
layout: example
order: 46
title: "Programming principles reviewed"
description: A shipment that answers for its amount due, read by two readers that agree until a credit is granted and then differ.
github_path: examples/46-appendix-f-programming-principles
card_eyebrow: "Appendices · Programming principles"
card_blurb: "One remittance line, read by a reader that asks the shipment and by a comparison reader that reaches through to the invoice. They agree until a credit is granted, and then only the reader that asks the shipment reports the amount due."
card_title: "Ask the shipment"
---

One small billing module carries the example. A `Shipment` holds an `Invoice` and the credits
granted against it, and `amount_due()` is the invoice total less each credit. `settle` accepts a
payment only when it equals the amount due.

## Two readers

`remittance_line` asks the shipment for `amount_due` and for `consignment_id`. The comparison
reader, `_chained_remittance`, names `consignment_id`, `invoice` and `total`. It lives in the
tests' conftest and not in the package, and a fixture runs the tests that take it with each
reader. With no credit the two give the same line. After a credit of 10.63 EUR against an invoice
of 35.63 EUR, the shipped reader gives `CN-3 25.00 EUR` and the comparison reader gives
`CN-3 35.63 EUR`.

## What the tests count

One test reads each reader's own source and lists the attribute names it uses. It does not count
the calls made inside those attributes.

## Build, run, observe

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from the example directory:

```bash
cd examples/46-appendix-f-programming-principles
uv run pytest -v
uv run mypy --strict src tests
```

The example README lists what each test verifies.
