# Testing baseline

A rating engine that asks carriers for a price, skips the ones that time out and books only the
cheapest. It's small enough to read in one sitting: the example exists to witness how pytest, pytest-mock and mypy
prove a claim, and what each kind of test double does and doesn't check. A test counts as evidence
for one named claim, and only once it has been seen to fail with the check it guards deleted.

## What it witnesses

Fixtures and parametrize.

- Fixtures supply dependencies by parameter name from `conftest.py`. `make_fake` is a factory
  fixture, and `quote_log` is a `yield` fixture whose teardown appends a line and prints its name; the
  chapter's third experiment shows that line printed for a failing test.
- `pytest.param(..., id=...)` names each case after the claim it carries.

What each double checks.

- A plain `Mock` passes an assertion on a misspelled method such as `bok`, so the assertion proves
  nothing.
- `Mock(spec=...)` rejects an unknown name but accepts a call with the wrong signature.
- `create_autospec(..., instance=True)` rejects both.
- mypy accepts every mock where a `CarrierGateway` is expected, and checks a hand-written fake. When
  the fake lacks one of two members, mypy prints a bare `[dict-item]` for a dict entry and adds a
  "missing following protocol member" note for an assignment.

Deterministic time and process state.

- `RateEngine` takes a `clock` and a `validity`, so `valid_until` is exact. Carriers are asked in
  code order and a tie goes to the smaller carrier code, so the winner never depends on mapping order.
- `validity_from_env` reads `RATE_QUOTE_VALIDITY_MINUTES`. The one test that touches the real
  environment does it inside `monkeypatch.context()` with `setenv` and `delenv`, and asserts the
  value is restored. Every other case passes an `environ` mapping.

mypy as a test.

- `uv run mypy --strict src tests` checks the tests too, including `assert_type`.
- `assert_type(1, str)` fails the mypy run and does nothing at runtime. The test carries a typed
  `# type: ignore[assert-type]`, which would itself fail under `warn_unused_ignores` if mypy stopped
  reporting.

## Layout

- `src/testing_baseline/domain.py`: `ConsignmentId`, `Weight`, `Money`, `Consignment`, `RatingError`.
- `src/testing_baseline/carriers.py`: `CarrierQuote`, `CarrierTimeoutError`, the `CarrierGateway`
  Protocol with `quote` and `book`.
- `src/testing_baseline/engine.py`: `RateQuote`, `RateEngine`, `validity_from_env`.
- `tests/conftest.py`: `FakeGateway`, `FakeFactory`, and the fixtures `consignment`, `fixed_now`,
  `make_fake` and `quote_log`.

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

Tests write only under pytest's `tmp_path`. None reads the wall clock or sleeps.

## What the tests verify

`tests/test_engine.py`

- `test_best_quote_picks_the_cheapest_carrier`: fastline-cheaper, airco-cheaper and an equal-amounts case that goes to airco.
- `test_a_tie_is_broken_by_the_carrier_code_in_the_quote`: with mapping keys that say nothing about the code, the smaller code still wins.
- `test_quote_validity_comes_from_the_injected_clock`: `valid_until` is the injected instant plus the validity; `assert_type(quote.total, Money)`.
- `test_a_timed_out_carrier_is_skipped`: the winner is the carrier that answered and the skipped code is reported.
- `test_carriers_are_asked_in_code_order`: skipped codes come back sorted whatever the mapping order.
- `test_every_carrier_timing_out_is_a_rating_error`: `RatingError("no carrier answered")`.
- `test_book_best_books_the_winner_and_returns_its_reference`: with fakes, only the winner records a booking.

`tests/test_doubles.py`

- `test_book_best_books_only_the_winner`: autospec doubles, `assert_called_once_with` on the winner and `assert_not_called` on the loser.
- `test_a_plain_mock_passes_an_assertion_on_a_misspelled_method`: `loser.bok.assert_not_called()` passes after `loser.book(...)` was called.
- `test_spec_rejects_unknown_names_but_not_wrong_signatures`: `AttributeError` for `bok`; `book()` with no argument is accepted.
- `test_autospec_rejects_names_and_signatures`: `AttributeError` for `bok`; `TypeError: missing a required argument: 'consignment'`.
- `test_a_fake_rejects_unknown_names_and_wrong_signatures`: `AttributeError` for `bok` and `TypeError` for `book()`; the two `# type: ignore` codes are mypy's `[attr-defined]` and `[call-arg]`.
- `test_side_effect_drives_the_timeout_branch`: `side_effect` raises `CarrierTimeoutError` and the engine skips that carrier.

`tests/test_environment.py`

- `test_validity_reads_the_environment_and_the_context_restores_it`: `setenv`, `delenv` and restoration inside `monkeypatch.context()`.
- `test_validity_defaults_to_thirty_minutes_when_unset`, `test_validity_accepts_a_positive_int`: through the `environ` parameter, no patching.
- `test_validity_rejects_a_value_that_is_not_a_positive_int`: zero, negative and text.

`tests/test_domain.py`

- `test_weight_rejects_a_mass_that_is_not_positive_and_finite`: zero, negative, NaN and infinity.
- `test_money_orders_by_amount_within_one_currency`, `test_money_refuses_to_order_across_currencies`.

`tests/test_static.py`

- `test_mypy_accepts_every_mock_where_a_gateway_is_expected`: `Mock`, `Mock(spec=)`, `MagicMock(spec=)` and autospec all exit 0 with no output.
- `test_mypy_checks_a_hand_written_fake`: `[dict-item]` with no protocol note, and `[assignment]` with `missing following "CarrierGateway" protocol member`.
- `test_assert_type_is_static_only`: `[assert-type]` from mypy, and `assert_type(1, str)` returns `1` at runtime.

Mocks bypass the static check, so a green mypy run says nothing about a mock. `FakeGateway` in
`tests/conftest.py` is the checked alternative.
