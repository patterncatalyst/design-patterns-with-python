# Three-way split

One shipping model, nineteen tests. Each test is a witness for a claim about a classic
design pattern in modern Python: the language feature reduces it to a few lines, the
pattern remains real design, or its name now means two things.

## What it witnesses

Dissolve: a language feature does the work.

- Strategy is a callable, so `quote(consignment, rule)` takes a function, a lambda or a
  `functools.partial`.
- Factory Method is a class in a dict (`GATEWAYS`).
- Iterator is a generator (`pages`).
- Template Method is a function that takes hooks (`declare_customs`).
- Builder is a keyword-only dataclass (`BookingRequest`).
- Prototype is `dataclasses.replace`.
- Visitor is `functools.singledispatch` (`describe`).
- Null Object is an optional that `mypy --strict` checks (`find_gateway`).
- Value Object is a frozen dataclass (`Money`).
- Registry is `__init_subclass__` (`CarrierBase`).

Survive: the design is still needed.

- A deferred call is a `functools.partial` in a `collections.deque`, but undo needs a
  command object (`Amendment`, `Booking`).

Disambiguate: one name, two mechanisms.

- The Decorator pattern wraps an object at runtime (`Surcharge` around `BaseRate`), while
  the `@` syntax rebinds a function name at definition time (`audited` on `quote_carrier`).
  The two are independent.
- Singleton is a module (`tariff_table`, `loads`).
- Lazy initialisation is `functools.cached_property` (`LazyTrackingHistory`).
- Proxy forwards only the attributes it does not define (`CarrierGatewayProxy`).
- Interface is a `Protocol` (structural), while an abstract base class is nominal.

## Layout

- `src/three_way_split/domain.py`: value types (`Consignment`, `Money`, `Weight`, the
  handling events, `RateQuote`, `TrackingHistory`, `Tariff`, customs types).
- `src/three_way_split/dissolve.py`: the dissolved patterns.
- `src/three_way_split/survive.py`: `Booking` and `Amendment`.
- `src/three_way_split/disambiguate.py`: the wrapper pattern, the `@` syntax, lazy
  initialisation and the proxy.
- `src/three_way_split/tariff_table.py` and `loads.py`: the module singleton and the log
  that counts its loads.

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

`tests/test_dissolve.py`

- `test_strategy_slot_accepts_def_lambda_and_partial`: a def, a lambda and a partial all fill the
  same `PricingRule` slot and return `Money`.
- `test_a_class_is_already_a_factory_method`: each `GATEWAYS` value is the gateway class itself,
  and calling it builds a new instance.
- `test_iterator_is_a_lazy_generator`: `pages` pulls nothing until asked, pulls exactly one page
  of items for the first page, returns itself from `iter`, and is exhausted after one pass.
- `test_template_method_is_a_function_taking_hooks`: the customs steps run in a fixed order and
  the hooks supply the varying parts.
- `test_builder_is_a_keyword_only_dataclass`: a positional `BookingRequest` call raises
  `TypeError`; every field is keyword-only.
- `test_prototype_is_replace`: `replace` returns a new consignment and leaves the original alone.
- `test_visitor_is_singledispatch_without_accept`: `describe` dispatches on each event class,
  falls back for other objects, and the event classes have no `accept` attribute.
- `test_null_object_is_an_optional_checked_by_mypy`: `mypy --strict` rejects an unguarded call
  on `find_gateway(...)` with `[union-attr]` and accepts the guarded one.
- `test_value_object_is_a_frozen_dataclass`: `Money` compares and hashes by value, rejects
  assignment, and adds only within one currency.
- `test_registry_is_init_subclass`: subclasses register by code, and a duplicate code raises
  `DuplicateCarrierError`.

`tests/test_survive.py`

- `test_deferred_command_is_a_partial_in_a_deque`: queued partials change nothing until they are
  called, then run in order.
- `test_undo_needs_a_command_object`: a partial has no `undo`; `Amendment` restores each earlier
  weight in reverse order.

`tests/test_disambiguate.py`

- `test_gof_decorator_wraps_an_instance_at_runtime`: a `Surcharge` is chosen per consignment,
  wraps the `BaseRate` without mutating it, has no base class and satisfies `RateCalculator`.
- `test_decorator_syntax_rebinds_the_name_at_definition_time`: `audited(sink)` replaces the
  function with a wrapper that keeps its name and reports each call.
- `test_the_two_decorators_are_independent`: an audited function inside a `Surcharge` stack is
  reported once per call, and neither mechanism adds the other's attributes.
- `test_module_is_one_instance_for_every_importer`: two imports return the same module and the
  same `TARIFF`, and the load log shows one load.
- `test_cached_property_is_lazy_initialisation_without_a_proxy`: the loader runs on first access
  only, and the value then lives in the instance dictionary.
- `test_proxy_forwards_only_missing_attributes`: `book` is answered from the proxy's cache, other
  attributes come from the wrapped gateway, and unknown names raise `AttributeError`.
- `test_protocol_is_structural_and_abc_is_nominal`: an unrelated class satisfies `CarrierGateway`
  but not `CarrierBase`, and an incomplete subclass of the base cannot be instantiated.
