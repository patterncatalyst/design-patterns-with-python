# Metaclasses, `__init_subclass__`, and registries

A registry of subclasses needs no metaclass. `CarrierBase.__init_subclass__` runs each time a
carrier class is created, takes the carrier code as a class keyword that mypy checks, and refuses
a bad class before it is registered. What remains to design is which classes register, what is
refused at definition, which modules must be imported for a registration to exist, and how tests
stay out of each other's way. The example books consignments through carrier gateways that other
teams add.

## What it witnesses

Registration by class keyword.

- `FastlineGateway(CarrierBase, code="FASTLINE")` and `AircoGateway(CarrierBase, code="AIRCO")`
  register when their modules are imported. `registry` is a read-only `MappingProxyType` view, and
  `gateway_for` books through it and raises `UnknownCarrierError` for an unknown code.
- `__init_subclass__` has a closed signature with no extra keywords, so mypy reports a misspelt
  class keyword with a suggestion, and checks the keyword's type.

Refusals at definition.

- A duplicate code raises `DuplicateCarrierError` and keeps the first class. A concrete class
  without a code and an abstract class with one raise `CarrierRegistrationError`. An unknown
  keyword raises `TypeError`. Every refusal leaves the registry unchanged.
- An abstract intermediate class is not registered. `inspect.isabstract` sees abstractness inside
  the hook, although `__abstractmethods__` is not set yet.
- `__set_name__` runs before `__init_subclass__`, and a class decorator runs after it.

Imports and test isolation.

- `carrier_registry/__init__.py` imports no carrier module. In a fresh interpreter the registry is
  empty until `airco` and then `fastline` are imported, and a concrete carrier under an abstract
  intermediate registers.
- `tests/conftest.py` imports both carrier modules once, and no test registers a carrier in the
  test process: every class a test defines under `CarrierBase` is abstract or is refused before
  insertion.

The metaclass form.

- `registry_form` is `init_subclass` or `metaclass`. `_CarrierMeta(ABCMeta)` in `conftest.py`
  applies the same four rules, and both forms pass one table of bookings and refusals.
- A second metaclass conflicts with an `ABC` or a `Protocol` base, and one derived from `ABCMeta`
  does not.
- Only a metaclass gives the class object operators: `in`, `list` and `len` work on
  `_MetaCarrierBase`, and `in` raises `TypeError` on `CarrierBase`.

mypy 2.4.1, on reduced models.

- It does not check a metaclass's class keywords, reports a metaclass conflict, refuses `Self` in a
  metaclass `__new__`, types a class called from a registry of metaclass instances as `Any`, and
  types a call by `__init__` although a metaclass `__call__` declares another return type.

## Layout

- `src/carrier_registry/carriers.py`: `ConsignmentId`, `DuplicateCarrierError`,
  `CarrierRegistrationError`, `UnknownCarrierError`, `CarrierBase`, `gateway_for`.
- `src/carrier_registry/fastline.py`: `FastlineGateway`.
- `src/carrier_registry/airco.py`: `AircoGateway`.

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

`tests/test_registry.py`

- `test_every_registry_form_books_through_the_registered_carrier`: `registry_form` and two codes.
- `test_every_registry_form_refuses_a_bad_carrier_class_and_keeps_the_registry`: `registry_form`
  and four refusals.
- `test_the_registry_maps_each_code_to_its_gateway_class`: the sorted code and class names.
- `test_gateway_for_books_with_the_registered_carrier`: `AC-CN-1`.
- `test_an_unknown_code_raises_unknown_carrier_error`: `unknown carrier 'NOPE'`.
- `test_the_carrier_registry_is_a_read_only_view`: item assignment refused.
- `test_a_duplicate_code_keeps_the_first_class`: the message names `FastlineGateway`.
- `test_an_abstract_intermediate_class_is_not_registered`: the registry is unchanged.
- `test_a_concrete_class_without_a_code_is_refused`: `Forgot is concrete and needs a code`.
- `test_isabstract_sees_abstractness_inside_init_subclass`: a test-local root records what the
  hook sees.
- `test_set_name_runs_before_init_subclass_and_a_class_decorator_after`: the logged order.
- `test_a_forgotten_manual_registration_leaves_the_carrier_unavailable`: a `KeyError`.
- `test_a_carrier_module_registers_only_when_it_is_imported`: a fresh interpreter, three dumps.
- `test_a_concrete_carrier_under_an_abstract_intermediate_registers`: a fresh interpreter.

`tests/test_metaclass.py`

- `test_a_second_metaclass_conflicts_with_the_bases_metaclass`: an `ABC` base and a `Protocol`
  base.
- `test_a_metaclass_derived_from_abcmeta_resolves_the_conflict`: nothing registers.
- `test_only_a_metaclass_gives_the_class_object_operators`: `in`, `list` and `len`, and the
  `TypeError` on `CarrierBase`.

`tests/test_static.py`

- `test_mypy_checks_the_type_of_a_class_keyword`: `[arg-type]`.
- `test_mypy_reports_a_misspelt_class_keyword`: `[call-arg]` and the suggestion.
- `test_mypy_does_not_check_metaclass_class_keywords`: exit 0, and an `int` key registered (a
  reduced model).
- `test_mypy_reports_a_metaclass_conflict`: `[metaclass]` and a run-time `TypeError` (a reduced
  model).
- `test_mypy_refuses_self_in_a_metaclass_new`: `[misc]`, and the class still builds (a reduced
  model).
- `test_mypy_types_a_class_called_from_a_metaclass_registry_as_any`: exit 0 and a run-time
  `AttributeError` (a reduced model).
- `test_mypy_ignores_a_metaclass_call_return_type`: exit 0 and a run-time `1` (a reduced model).

Classes and functions named with a leading underscore in the tests are fixtures and aren't part
of the model code.
