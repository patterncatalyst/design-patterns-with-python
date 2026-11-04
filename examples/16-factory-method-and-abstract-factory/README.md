# Factory Method and Abstract Factory

A gateway per carrier resolved by code, and a kit of products per carrier family. The chapter's
thesis is that Factory Method dissolves and Abstract Factory survives: a class or a `Self`
classmethod in a `Callable` slot is already a factory, while keeping products from one family
together is a design decision that no language feature makes for you. Rates, accounts and
endpoints are illustrative.

## What it witnesses

Factory Method.

- `GATEWAYS` is a read-only `frozendict` from carrier code to a `GatewayFactory`, a
  `Callable[[CarrierSettings], CarrierGateway[str]]`. Each entry is a `from_settings` classmethod
  that returns `Self`, so a subclass builds itself and not the parent.
- `make_gateway` turns an unknown code into an `UnknownCarrierError`.
- A GoF creator hierarchy (`_BookingDesk` with two subclasses) is kept in a test as a comparison. It
  passes the same carrier table, with three classes where `factories.py` declares none.
- mypy checks a `Callable` slot against every constructor, including a classmethod that wants a
  different argument. A `type[CarrierGateway[str]]` slot accepts a class that needs an argument and
  lets the zero-argument call through, which fails at run time. It rejects a `partial` and the
  Protocol itself.

Abstract Factory.

- A carrier added to two of three if-chains is quoted at another carrier's rate, and mypy is
  silent while the code is a `str`. The if-chains are a test fixture, and the two snippets in
  `test_static.py` that stand for them are reduced models.
- `CarrierKit[R]` is a frozen slotted value holding the constructors of one family. The reference
  type `R` ties the gateway to the label printer: a kit that mixes a Fastline gateway with an Airco
  label printer is a `[misc]` error. `KITS` hides `R` behind the one-method `Shipper` Protocol.
- The tie covers only products that pass values to each other. A kit with another carrier's rates
  and a label printer that takes any `str` are both accepted. A kit assembled by hand under a
  `type: ignore` prints a Fastline reference on an Airco label.

## Layout

- `src/factories/domain.py`: `ConsignmentId`, `Money`, `CarrierSettings`, `CarrierQuote`,
  `Shipment`, `UnknownCarrierError`.
- `src/factories/carriers.py`: `FastlineReference`, `AircoReference`, the `CarrierGateway[R]`,
  `LabelPrinter[R]` and `RateSource` Protocols, and the products of each carrier.
- `src/factories/factories.py`: `GatewayFactory`, `GATEWAYS`, `make_gateway`.
- `src/factories/kits.py`: `CarrierKit`, `Shipper`, `FASTLINE_KIT`, `AIRCO_KIT`, `KITS`, `ship`.

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

`tests/test_factory_method.py`

- `test_a_registered_constructor_builds_each_carrier_gateway`: the registry and the creator hierarchy give the same reference for each carrier.
- `test_a_classmethod_constructor_returns_the_subclass_it_is_called_on`: a subclass of `AircoGateway` builds itself.
- `test_a_sandbox_setting_selects_the_sandbox_endpoint`: the Fastline endpoint follows `sandbox`.
- `test_an_unknown_carrier_code_is_an_unknown_carrier_error`: both registries, with the original `KeyError` suppressed.
- `test_the_carrier_registries_are_read_only`: item assignment raises `TypeError` and neither is a `dict`.
- `test_the_creator_design_declares_three_classes_where_the_registry_declares_none`: an `ast` count.
- `test_a_type_registry_accepts_a_class_that_cannot_be_called_without_arguments`: the Airco call fails at run time.

`tests/test_if_chains.py`

- `test_a_carrier_missing_from_one_if_chain_is_quoted_at_another_carriers_rate`: 12.00 where the kit gives 48.00.

`tests/test_kits.py`

- `test_each_kit_ships_with_its_own_carriers_products`: reference, label and quote for each carrier.
- `test_a_hand_mixed_kit_prints_one_carriers_reference_on_anothers_label`: `AIRCO FL-CN-1`.
- `test_every_kit_is_a_frozen_value`: assignment is refused and equal kits compare equal.

`tests/test_static.py`

- `test_mypy_checks_a_constructor_slot_but_not_a_type_slot`: four slots, four results.
- `test_mypy_checks_a_classmethod_constructor_against_the_slot`: `[dict-item]`.
- `test_mypy_cannot_see_a_carrier_missing_from_an_if_chain`: clean for a `str` code, `[arg-type]` for a `Literal` code.
- `test_mypy_rejects_a_kit_that_mixes_reference_types`: `[misc]`.
- `test_mypy_accepts_kits_that_mix_untied_products`: another carrier's rates, and a printer that takes any `str`.
- `test_mypy_rejects_a_kit_registry_typed_by_one_family`: `[dict-item]`.

Classes named with a leading underscore in the test modules are test fixtures and aren't part of
the model code.
