# Mocking reference

The tests in this example show the `unittest.mock` and pytest-mock API the book's suites rely on,
each on the pinned Python and pytest-mock. Mocks appear only in the tests, and only because the mock
API is the subject. The source holds no mock and no patch.

A fake passed as a parameter is the book's first choice. `create_autospec` comes next, for the
case where the calls are the claim. A patch is the last resort, for a name with no parameter to
pass. A mock is assignable to every type, so mypy has nothing to check at the call site; the
static tests show what it does report.

## What it witnesses

The module under test is small. `CarrierGateway` is a protocol with `quote` and `book`.
`FastlineGateway` implements it with a fixed rate per kilogram and a timeout above a weight limit.
`confirm` is an async function. `book_cheapest` asks each carrier in code order, skips a carrier
that times out, books the cheapest by total and then carrier name, and passes the reference to a
`notify` callback.

| Area | What the tests show |
| --- | --- |
| Making a double | `spec_set`, `seal`, the assertion-typo refusal and `unsafe`, `MagicMock`, `wraps` and `AsyncMock` |
| Configuring and inspecting | `side_effect` as an iterable and as a callable, `mock_calls`, `call_args_list`, `ANY`, `assert_has_calls` and `reset_mock` |
| Patching | `mocker.patch.object` with `autospec`, `mocker.patch.dict`, `mocker.stop` and the context-manager warning |
| Spies and stubs | `mocker.spy` returns and exceptions, `mocker.stub` and `mocker.resetall` |
| Async | an autospec of an `async def` records the await |
| Static | the types mypy gives `mocker` objects, and a stub where a callback is expected |

## Layout

- `src/mocking_reference/carriers.py`: `ConsignmentId`, `CarrierQuote`, `CarrierTimeoutError`,
  `CarrierGateway`, `FastlineGateway`, `confirm`.
- `src/mocking_reference/booking.py`: `Notify`, `book_cheapest`.
- `tests/conftest.py`: the `fastline` fixture, a real gateway.

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

`tests/test_doubles.py`

- `test_spec_set_refuses_setting_a_name_the_spec_lacks`: `spec` allows the assignment.
- `test_seal_stops_new_attributes_on_a_configured_mock`
- `test_an_assertion_typo_raises_instead_of_passing`: `unsafe=True` allows the name.
- `test_a_magic_mock_supports_the_magic_methods_a_mock_lacks`
- `test_wraps_passes_calls_through_to_the_real_gateway`
- `test_async_mock_return_value_is_awaited`

`tests/test_calls.py`

- `test_side_effect_iterable_returns_each_value_then_raises_stop_iteration`
- `test_side_effect_callable_computes_the_return_value`
- `test_mock_calls_records_calls_in_order_with_call_objects`: `book_cheapest` over two autospecs
  attached to one manager.
- `test_call_args_list_and_any_match_arguments`
- `test_assert_has_calls_checks_a_contiguous_ordered_run`: a run with a gap fails, and
  `any_order=True` accepts it.
- `test_reset_mock_clears_calls_but_keeps_return_value`: once by default and once with
  `return_value=True`.

`tests/test_booking.py`

- `test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first`
- `test_a_carrier_that_times_out_is_skipped`
- `test_every_carrier_timing_out_raises_lookup_error`

`tests/test_patching.py`

- `test_patch_object_replaces_an_attribute_for_the_test`: with `autospec=True` a call with the
  wrong arguments is refused.
- `test_patch_dict_restores_the_mapping_after_the_test`: once for a key that was absent and once
  for a key that was present.
- `test_mocker_stop_undoes_one_patch`
- `test_mocker_patch_used_as_a_context_manager_fails_under_the_warning_filter`

`tests/test_spies.py`

- `test_spy_keeps_the_real_behaviour_and_records_returns`
- `test_spy_records_the_exception_it_let_through`
- `test_stub_records_a_callback`
- `test_resetall_resets_patches_spies_and_autospecs_but_not_stubs`
- `test_autospec_of_an_async_function_records_the_await`

`tests/test_static.py`

- `test_mypy_types_mocker_objects_as_mocks`: one case each for `patch`, `patch.object`, `spy`,
  `stub` and `Mock`.
- `test_mypy_accepts_a_stub_where_a_callback_is_expected`

The context-manager test needs the root `filterwarnings = ["error"]`: under a lenient filter the
warning is only reported. No test sleeps or reads a clock. The static tests run
`mypy --strict --warn-unreachable` through `mypy.api`.
