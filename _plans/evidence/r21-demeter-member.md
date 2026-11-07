---
title: "r21 evidence: the Appendix F member"
output: false
---

# r21 evidence: `examples/46-appendix-f-programming-principles`

Recorded 2026-11-07 at branch `release/r21`, base commit 479f0ba, with the member uncommitted. Outputs are scrubbed (`<repo>` for the checkout path). Python 3.15.2, uv 0.13.7, pytest 9.2.0, mypy 2.4.1, ruff 0.17.4.

## Build record

```text
$ uv init --lib --vcs none --no-readme --no-description --author-from none --name principles-reviewed examples/46-appendix-f-programming-principles
Project `principles-reviewed` is already a member of workspace `<repo>`
Initialized project `principles-reviewed` at `<repo>/examples/46-appendix-f-programming-principles`
```

It created `pyproject.toml`, `src/principles_reviewed/__init__.py` and `src/principles_reviewed/py.typed`. The two edits of Appendix A: `requires-python = ">=3.15.2"` became `">=3.15"`, and `uv_build>=0.13.7,<0.14.0` became `uv_build>=0.13.7,<0.14`. The generated `hello()` was removed and `__init__.py` is empty.

```text
$ uv lock
Resolved 57 packages in 110ms
Added principles-reviewed v0.1.0
$ uv lock --check
Resolved 57 packages in 1ms
```

The only `uv.lock` change is the new member: the entry `principles-reviewed` in the root's package list, a `[[package]]` block with `source = { editable = "examples/46-appendix-f-programming-principles" }`, and the workspace members line. `git diff --stat uv.lock` shows 6 insertions and no deletion.

## Counts, from fresh runs

The member has 12 test functions and 18 cases: `test_billing.py` 8 functions and 9 cases, `test_demeter.py` 4 functions and 9 cases. The plan's 9 functions and 15 cases grew by three tests the source pins (see "Additions").

From the member directory, three runs of `uv run pytest` and of `uv run mypy --strict src tests`:

```text
18 passed in 0.03s   (three times)
Success: no issues found in 6 source files   (three times)
```

Reverse file order, from the member (`pytest tests/test_demeter.py tests/test_billing.py`) and from the root (`uv run pytest examples/46-appendix-f-programming-principles/tests/test_demeter.py examples/46-appendix-f-programming-principles/tests/test_billing.py -q`):

```text
18 passed in 0.03s
18 passed in 0.02s
```

From the root, `uv run pytest examples/46-appendix-f-programming-principles -q` three times:

```text
18 passed in 0.02s   (three times)
```

Whole repository: `uv run pytest --co -q` ends `1405 tests collected in 0.47s`, with no error. `bash scripts/verify.sh` prints `1405 passed in 162.84s (0:02:42)` and `verify: all steps passed` (1387 before the member, plus 18).

`uv run ruff check .` printed `All checks passed!` and `uv run ruff format --check .` printed `6 files already formatted` in the member. The idiom scan over `src` and `tests`:

```text
total: 0 matching lines (0 ban-tier) under examples/46-appendix-f-programming-principles/src examples/46-appendix-f-programming-principles/tests
```

## The `src` grep of the rejected list

```text
$ grep -rnE '\bAny\b|\bcast\b|Optional|print\(|random|\bglobal\b|time\.|datetime|sys\.modules|subprocess|socket|urllib|http|mock|monkeypatch' examples/46-appendix-f-programming-principles/src
$ grep -rnE '\b(self)\.\w+\.\w+\.\w+|\b(shipment|payment|due|invoice|credit|line|other|first)\.\w+\.\w+' examples/46-appendix-f-programming-principles/src
```

Both print nothing: no attribute chain in `src` runs from a parameter or `self` past an immediate part. In `tests`, `grep -rnE 'time\.|random|sleep|datetime|socket|urllib'` prints nothing, and `_chained_remittance` appears only in `tests/conftest.py` (its definition and the table of readers).

## Deletion table

Each row ran in its own fresh scratch copy (the tracked and untracked files, `.venv` and `.venv-ft` removed, `uv sync --locked --all-packages`, `principles_reviewed.__file__` confirmed inside the copy), against `pytest examples/46-appendix-f-programming-principles`, and the copy was deleted afterwards. Rows 1 to 9 are the plan's table; rows 10 to 12 cover the three additions.

| Row | Changed as | Result | Failing tests |
| --- | --- | --- | --- |
| 1 | `amount_due` loop body removed | 7 failed, 11 passed | `test_the_amount_due_subtracts_the_credits`, `test_a_credit_in_another_currency_is_refused`, `test_settle_accepts_the_amount_due`, `test_settle_refuses_any_other_payment` (both), `test_settle_refuses_the_right_amount_in_another_currency`, `test_a_credit_reaches_only_the_reader_that_asks_the_shipment[delegating]` |
| 2 | `remittance_line` reads `shipment.invoice.total` | 2 failed, 16 passed | `test_a_credit_reaches_only_the_reader_that_asks_the_shipment[delegating]`, `test_each_reader_names_the_attributes_it_depends_on[delegating]` |
| 3 | `_chained_remittance` calls `shipment.amount_due()` | 2 failed, 16 passed | `test_a_credit_reaches_only_the_reader_that_asks_the_shipment[chained]`, `test_each_reader_names_the_attributes_it_depends_on[chained]` |
| 4 | `Money.__add__` currency check removed | 1 failed, 17 passed | `test_lines_in_two_currencies_have_no_total` |
| 5 | `Money.__sub__` currency check removed | 1 failed, 17 passed | `test_a_credit_in_another_currency_is_refused` |
| 6 | `Money.__str__` drops the currency | 9 failed, 9 passed | `test_settle_refuses_any_other_payment` (both), `test_settle_refuses_the_right_amount_in_another_currency`, `test_both_readers_give_the_same_line_without_credits` (four), `test_a_credit_reaches_only_the_reader_that_asks_the_shipment` (both) |
| 7 | `settle` tests `payment.amount < due.amount` | 2 failed, 16 passed | `test_settle_refuses_any_other_payment[25.01]`, `test_settle_refuses_the_right_amount_in_another_currency` |
| 8 | `Invoice.total` returns the first line | 11 failed, 7 passed | `test_an_invoice_totals_its_lines`, `test_lines_in_two_currencies_have_no_total`, `test_the_amount_due_subtracts_the_credits`, `test_settle_accepts_the_amount_due`, `test_settle_refuses_any_other_payment` (both), `test_settle_refuses_the_right_amount_in_another_currency`, `test_both_readers_give_the_same_line_without_credits[delegating-two-lines]` and `[chained-two-lines]`, `test_a_credit_reaches_only_the_reader_that_asks_the_shipment` (both) |
| 9 | `credited` fixture without its credit | 6 failed, 12 passed | `test_the_amount_due_subtracts_the_credits`, `test_settle_accepts_the_amount_due`, `test_settle_refuses_any_other_payment` (both), `test_settle_refuses_the_right_amount_in_another_currency`, `test_a_credit_reaches_only_the_reader_that_asks_the_shipment[delegating]` |
| 10 | `Invoice.__post_init__` guard removed | 1 failed, 17 passed | `test_an_invoice_needs_a_line` |
| 11 | `settle` tests `payment.amount != due.amount` | 1 failed, 17 passed | `test_settle_refuses_the_right_amount_in_another_currency` |
| 12 | `_chained_remittance` added to `billing.py` | 1 failed, 17 passed | `test_the_comparison_reader_is_not_part_of_the_package` |

## Differences from the plan's table

- Rows 1, 6, 7, 8 and 9 each fail one test more than the plan's count, and in each case it is `test_settle_refuses_the_right_amount_in_another_currency` (row 7: the plan's one failure plus that test; row 8: ten plus that test). Row 7 now has two failures because a payment of 25.00 USD against 25.00 EUR is accepted when only the amounts are compared.
- Rows 2 to 5 match the plan exactly.

## Additions

The plan's spec pinned three behaviours that none of its nine tests saw, so three tests were added: `test_an_invoice_needs_a_line` (the guard in `Invoice.__post_init__`, row 10), `test_settle_refuses_the_right_amount_in_another_currency` (payment equality includes the currency, row 11) and `test_the_comparison_reader_is_not_part_of_the_package` (the README and card say the comparison reader lives only in `tests/conftest.py`, row 12). The plan's count of 9 functions and 15 cases is therefore 12 functions and 18 cases.

## The final project's chains

`grep -n` at the branch head:

```text
examples/39-final-project/tests/test_acceptance.py:40:    if shipment.invoice.total != Money(Decimal("35.63")):
examples/39-final-project/tests/test_acceptance.py:41:        failures.append(f"invoice {shipment.invoice.total.amount}")
examples/39-final-project/tests/test_parts.py:98:        totals.append((shipment.quote.total, shipment.invoice.total))
examples/39-final-project/src/final_project/desk.py:58:            HandlingEvent(consignment.id, HandlingKind.BOOKED, self._plan.sailing.origin)
examples/39-final-project/src/final_project/billing.py:39:        raise SettlementError(f"{payment.amount} does not settle {invoice.total.amount}")
```

`grep -rni credit examples/39-final-project/src` prints nothing: the final project grants no credit. The helper `acceptance_failures` in `test_acceptance.py` takes `shipment` as a parameter; `desk.py:58` reads `self._plan.sailing.origin`, an object returned by an immediate part. `billing.py:39` formats `invoice.total.amount` from its parameter, a fifth line that the plan's evidence also records.
