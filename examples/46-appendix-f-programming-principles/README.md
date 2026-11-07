# Programming principles reviewed

This example witnesses one principle that no other chapter's tests show: the Law of Demeter. A
shipment answers `amount_due()`. The reader the package ships, `remittance_line`, asks the shipment
for it. The comparison reader reaches through the shipment to its invoice. The two give the same
line until a credit is granted; after that, only the reader that asks the shipment reports the
amount due.

The comparison reader, `_chained_remittance`, lives in `tests/conftest.py` and is not part of the
package. A conftest fixture, `reader_form`, runs the tests that take it once with each reader.

## What it witnesses

The module under test is small. `Money` is an amount in one currency. `LineItem` pairs a
description with an amount. `Invoice` holds line items and totals them. `Shipment` holds an invoice
and the credits granted against it, and `amount_due()` is the invoice total less each credit.
`settle` accepts a payment only if it equals the amount due, and `remittance_line` formats the
consignment identifier and the amount due.

| Area | What the tests show |
| --- | --- |
| The two readers agree | with no credit, both give `CN-1 30.00 EUR` and `CN-2 35.63 EUR` |
| A credit reaches one reader | `CN-3` with a 10.63 EUR credit gives `CN-3 25.00 EUR` from the reader that asks the shipment and `CN-3 35.63 EUR` from the one that reaches through |
| What each reader names | `amount_due` and `consignment_id` against `consignment_id`, `invoice` and `total` |
| Money and settlement | totals, refusal of a second currency, the amount due, and the payments `settle` refuses |

## Layout

- `src/principles_reviewed/domain.py`: `ConsignmentId`, `Money`.
- `src/principles_reviewed/billing.py`: `LineItem`, `Invoice`, `Shipment`, `SettlementError`,
  `settle`, `remittance_line`.
- `tests/conftest.py`: `_chained_remittance`, the table of readers, the `reader_form` fixture and
  the `credited` fixture.

## Run it

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from this directory:

```bash
uv run pytest
uv run mypy --strict src tests
```

## What the tests verify

`tests/test_billing.py`

- `test_an_invoice_totals_its_lines`
- `test_an_invoice_needs_a_line`
- `test_lines_in_two_currencies_have_no_total`
- `test_the_amount_due_subtracts_the_credits`
- `test_a_credit_in_another_currency_is_refused`
- `test_settle_accepts_the_amount_due`
- `test_settle_refuses_any_other_payment`: once for 24.99 and once for 25.01.
- `test_settle_refuses_the_right_amount_in_another_currency`

`tests/test_demeter.py`

- `test_both_readers_give_the_same_line_without_credits`: two invoices, each read by both readers.
- `test_a_credit_reaches_only_the_reader_that_asks_the_shipment`: the chained case pins the
  invoice total, which is the comparison reader's answer, as a literal.
- `test_each_reader_names_the_attributes_it_depends_on`: the attribute names a reader's own source
  uses. It does not count the calls made inside those attributes.
- `test_the_comparison_reader_is_not_part_of_the_package`: the package holds two modules and
  neither defines `_chained_remittance`.
