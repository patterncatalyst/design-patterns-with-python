# Decorator the pattern vs @decorator the syntax, and Proxy

Three things that look like a wrapper and are not the same. The Decorator pattern is a wrapper
object with the wrapped object's interface, composed while the program runs, so a stack of layers
is data. The `@decorator` syntax rebinds a function name once, at definition time. A proxy keeps
the interface and controls access. The chapter's thesis is that the two decorator names need
disambiguating and that the proxy to prefer is an explicit class mypy can check. Rates, fees, tax
percentages and the retry count are illustrative. `functools.wraps` and `ParamSpec` are used in
`retry` and `audited` and are not taught here.

## What it witnesses

The Decorator pattern.

- `BaseRate`, `Discount`, `Surcharge` and `Tax` are frozen dataclasses with no base class. Each
  satisfies the `RateCalculator` Protocol and wraps another one without changing it. Money rounds
  half-up to cents in `Money.scaled`, and `Money.__add__` refuses another currency.
- Order matters once there is an additive fee: for 100 kg at 1.20 with a 15.00 fee, tax outside
  gives 163.35, fee outside 160.20, discount outside 121.50 and fee outside the discount 123.00.
  Two percentage layers agree before rounding (130.68 both ways at 120.00) and split by a cent
  after it (0.06 against 0.05 at 0.05 per kilogram). The sweep is in
  `_plans/evidence/percentage-layer-rounding.md`.
- `compose(base, layers)` puts the last layer outermost, and `layers_for(consignment)` chooses the
  layers while the program runs: heavy and dangerous-goods surcharges first, destination tax last,
  and an unknown country is a `RatingError`. A stack compares and hashes by value.
- The layer constructors (`discount`, `surcharge`, `tax`) return small lambdas.

The `@decorator` syntax.

- `retry` and `audited` are PEP 695 `[**P, R]` factories. `quote_carrier` carries
  `@retry(attempts=3, on=(CarrierTimeoutError,))`. A test-local counting decorator shows the
  factory runs once at definition, and `__wrapped__` isn't the rebound name.
- `retry` calls again on a listed error, gives up after the last attempt, lets other errors
  through and refuses fewer than one attempt. It has no delay: backoff is out of scope.
- Stacking order is fixed when the `def` runs. An `@audited` above an `@retry` reports once for a
  quote that needed three calls, and the reverse reports once per attempt.
- Rebound functions don't compare by value. A decorated function has no `price`, and a layer has
  no `__wrapped__`. A factory such as `functools.cache` may return an object that isn't a function,
  and it is still the syntax.
- `ParamSpec` keeps the call signature for mypy: a wrong argument type is `[arg-type]` and an
  unknown keyword is `[call-arg]`.

Proxy.

- `CarrierGatewayProxy` caches `quote` in a per-instance dict, so it asks the gateway once per
  consignment, never stores a timeout, and forwards every `book`. The cache is single-threaded.
  mypy reports `[assignment]` with the missing protocol member for a copy of the proxy without `book`.
- `_ForwardingGatewayProxy` is a fixture in `tests/conftest.py`: it defines `quote` and forwards the
  rest with `__getattr__ -> Any`. It passes the same proxy table as the explicit form. mypy accepts a
  typo and a wrongly typed use through it, a `-> object` version fails the Protocol, a
  `runtime_checkable` `isinstance` is false because it looks attributes up statically, and a typo
  raises an `AttributeError` that names the wrapped class.
- The reduced-model snippets in `test_static.py` (the forwarding proxy with a typo or a wrong type, the
  forwarding proxy returning `object`, the proxy without `book`) are reduced models: they restate
  the shape and don't import the fixture.

## Layout

- `src/decorator_proxy/domain.py`: `ConsignmentId`, `Weight`, `Money`, `Consignment`,
  `CarrierQuote`, `RatingError`, `CarrierTimeoutError`.
- `src/decorator_proxy/layers.py`: `RateCalculator`, `BaseRate`, `Discount`, `Surcharge`, `Tax`,
  `Layer`, `discount`, `surcharge`, `tax`, `compose`, `layers_for`, `TAX_RATES`, `HEAVY_FEE`,
  `DANGEROUS_GOODS_FEE`, `HEAVY_OVER`.
- `src/decorator_proxy/syntax.py`: `retry`, `audited`, `quote_carrier`.
- `src/decorator_proxy/proxy.py`: the `CarrierGateway` Protocol and `CarrierGatewayProxy`.

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

`tests/test_layers.py`

- `test_a_layer_wraps_a_calculator_and_leaves_it_unchanged`: the inner calculator is the same object and prices as before.
- `test_layer_order_changes_the_price_when_a_fee_is_added`: four stacks, four prices.
- `test_two_percentage_layers_agree_before_rounding_and_can_split_by_a_cent`: 130.68 both ways, then 0.06 against 0.05.
- `test_the_layers_for_a_consignment_are_chosen_while_the_program_runs`: light, heavy and dangerous goods.
- `test_the_heavy_threshold_is_exclusive`: exactly the limit gets no surcharge.
- `test_the_fees_are_in_the_order_the_rules_say`: tax outermost, then dangerous goods, then heavy.
- `test_an_unknown_destination_country_is_a_rating_error`: no silent zero tax.
- `test_layer_stacks_compare_by_value`: equal, same hash, a different percentage is unequal.
- `test_compose_wraps_the_last_layer_outermost`: the type at each level.
- `test_a_layer_refuses_a_fee_in_another_currency`: `RatingError`.
- `test_a_weight_that_is_not_positive_and_finite_is_refused`: zero, negative and NaN.
- `test_the_tax_rates_are_read_only`: item assignment raises `TypeError` and the registry is not a `dict`.

`tests/test_syntax.py`

- `test_the_at_sign_rebinds_the_name_once_at_definition_time`: the factory ran once, at the `def`.
- `test_retry_calls_again_on_a_listed_error_and_gives_up_after_the_last_attempt`: three calls either way.
- `test_retry_lets_an_unlisted_error_through`: one call.
- `test_retry_refuses_fewer_than_one_attempt`: zero and negative.
- `test_audited_reports_each_call_to_the_injected_sink`: one report per call.
- `test_syntax_stacking_order_decides_whether_each_attempt_is_audited`: one report against three.
- `test_rebound_functions_do_not_compare_by_value`: two rebindings differ, equal stacks do not.
- `test_a_decorated_function_has_no_price_and_a_layer_has_no_wrapped`: neither mechanism has the other's attribute.
- `test_a_decorator_may_return_an_object_that_is_not_a_function`: `functools.cache`.

`tests/test_proxy.py`

- `test_the_proxy_asks_the_gateway_once_per_consignment`: both proxy forms.
- `test_the_proxy_forwards_every_booking`: both proxy forms, two bookings reach the gateway.
- `test_a_timed_out_quote_is_not_cached`: both proxy forms.
- `test_a_proxy_returns_what_the_gateway_returns_where_a_layer_changes_the_price`: the contrast with `Tax`.
- `test_runtime_checkable_does_not_see_attributes_forwarded_by_getattr`: explicit true, forwarding false.
- `test_a_forwarded_typo_is_reported_against_the_wrapped_gateway`: the message names `ScriptedGateway`.

`tests/test_static.py`

- `test_mypy_rejects_a_decorated_function_where_a_calculator_belongs`: `[assignment]`.
- `test_mypy_checks_each_layer_in_a_stack`: `[assignment]` for a wrapper without `price`, `[call-arg]` with a suggestion for a misspelt keyword.
- `test_mypy_keeps_the_call_signature_through_retry`: `[arg-type]` and `[call-arg]`.
- `test_mypy_accepts_the_explicit_proxy_as_a_gateway`: clean.
- `test_mypy_reports_a_typo_on_the_explicit_proxy`: `[attr-defined]`.
- `test_mypy_reports_a_member_missing_from_an_explicit_proxy`: `[assignment]`, naming `book` (a reduced model).
- `test_mypy_accepts_a_typo_through_a_forwarding_proxy`: clean for a typo and for a wrong type (a reduced model).
- `test_mypy_rejects_a_forwarding_proxy_that_returns_object`: `[assignment]`, `got "object"` (a reduced model).

Classes and functions named with a leading underscore in `tests/conftest.py`, and `ScriptedGateway`, are
test fixtures and aren't part of the model code.
