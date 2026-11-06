# singledispatch: the Visitor the language gives you

For an open set of kinds, Visitor's `accept` method and visitor class dissolve into one generic
function: `functools.singledispatch` holds an implementation per class and picks the most specific
one by the method resolution order. What remains to design is what the fallback does, registering by
annotation so the class and the parameter cannot disagree, defining classes before registering, and
knowing that a registration exists only once its module is imported. The example looks up customs
tariff codes by commodity kind and prices container surcharges by container kind. Headings and rates
are illustrative.

## What it witnesses

One function, one implementation per kind.

- `tariff_code` has an `object` fallback that raises `TariffCodeError` and names the kind, and
  registered implementations for `Coffee`, `InstantCoffee` and `TShirt`.
- `fallback_form` is `raising` or `defaulting`: `tariff_code`, and a dispatcher whose fallback
  returns `"unclassified"` over the same implementations. Both give seven commodities the same
  codes on one table. Only the raising form refuses a `LithiumIonBattery`, and the defaulting form
  answers without an error.
- The most specific registration wins. An unregistered subclass takes its base class's code. `dispatch`
  and the read-only `registry` show the choice, and the registry cannot be edited.
- A union annotation registers each member, and `register(cls, fn)` registers an existing function.

Registration and the module that loads.

- A generic alias is refused at registration. An annotation naming a class defined later raises
  `TypeError` at the decorator, with the address in the message masked in the test.
- `dangerous_goods` is another team's module that registers `LithiumIonBattery`. In a fresh
  interpreter a battery raises before the module is imported and gets `8507.60` after it.
- No test registers on `tariff_code`. Registration tests use `fresh_dispatcher`, a new raising
  dispatcher per test.

`singledispatchmethod` and mypy.

- `SurchargeSchedule.surcharge` dispatches on `DryContainer`, `ReeferContainer` and `TankContainer`,
  and on the argument after `self`: a `5` in that position takes the fallback, which raises
  `SurchargeError`.
- mypy 2.4.1 checks calls and registrations against the fallback's signature, and with an `object`
  fallback `tariff_code(42)` passes. A union fallback refuses a foreign kind. A `register(cls, fn)`
  whose class differs from the parameter, and a forward reference, pass mypy and fail at run time.
  mypy does not check the arguments of a `singledispatchmethod`.

## Layout

- `src/singledispatch_visitor/commodities.py`: `Coffee`, `InstantCoffee`, `TShirt`,
  `LithiumIonBattery`.
- `src/singledispatch_visitor/tariff.py`: `TariffCodeError`, `tariff_code`.
- `src/singledispatch_visitor/dangerous_goods.py`: the registration for `LithiumIonBattery`.
- `src/singledispatch_visitor/surcharges.py`: `DryContainer`, `ReeferContainer`, `TankContainer`,
  `SurchargeError`, `SurchargeSchedule`.
- `src/singledispatch_visitor/money.py`: `Money`.

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

`tests/test_tariff.py`

- `test_every_fallback_form_gives_registered_commodities_their_codes`: `fallback_form` and seven
  commodities.
- `test_a_raising_fallback_names_an_unregistered_kind`: `LithiumIonBattery` in the message.
- `test_a_defaulting_fallback_gives_an_unregistered_kind_a_code_silently`: `"unclassified"`.
- `test_the_most_specific_registration_wins`: `dispatch(InstantCoffee)`.
- `test_an_unregistered_subclass_gets_its_base_class_code`: a fresh dispatcher.
- `test_dispatch_and_registry_show_the_chosen_implementation`: the four keys, and `bool`.
- `test_the_registry_is_read_only`: item assignment refused, no `unregister`.

`tests/test_registration.py`

- `test_a_union_annotation_registers_each_member`: on a fresh dispatcher.
- `test_register_with_a_class_and_a_function_registers_the_function`: the function is returned.
- `test_a_generic_alias_is_refused_at_registration`: `is not a class`.
- `test_another_module_extends_the_set_when_it_is_imported`: a fresh interpreter, before and after.

`tests/test_surcharges.py`

- `test_surcharge_dispatches_on_the_container_kind`: dry, reefer and tank.
- `test_singledispatchmethod_dispatches_on_the_first_argument_after_self`: days vary, `5` falls back.

`tests/test_static.py`

- `test_mypy_checks_calls_and_registrations_against_the_fallback`: `[arg-type]`, `[assignment]` and
  `[call-arg]`, and `tariff_code(42)` passes.
- `test_mypy_refuses_a_kind_outside_a_union_fallback`: a reduced model.
- `test_mypy_accepts_a_registered_class_that_differs_from_the_parameter`: exit 0 and a run-time
  `AttributeError` (a reduced model).
- `test_mypy_accepts_a_forward_reference_that_fails_at_registration`: exit 0 and a run-time
  `TypeError` (a reduced model).
- `test_mypy_does_not_check_the_arguments_of_a_singledispatchmethod`: exit 0 and a run-time
  `TypeError`.

Classes and functions named with a leading underscore in the tests are fixtures and aren't part
of the model code.
