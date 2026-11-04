# Protocol and structural typing

Carrier lookup, pricing rules and quoters written against `Protocol`, `X | None` and an ABC. Each
test witnesses a claim about what mypy checks, what the runtime checks and what neither does. The
chapter's thesis is that an interface is a shape compared where a value is used, and that Null
Object dissolves into an optional return.

## What it witnesses

Absence in the type.

- `find_gateway` returns `CarrierGateway | None`. Unguarded access is `[union-attr]`; a walrus,
  `match`, an early return and `assert` each narrow it. `assert` is removed under `-O`.
- A do-nothing gateway returns an empty reference, loses the booking and passes `mypy --strict`.
  `no_discount` is a null object that is correct, because zero is the right discount.
- `ACCOUNT_DEFAULT` is a 3.15 `sentinel` that separates "not given" from `None`. It is truthy,
  survives `copy.copy` and narrows with `is`.
- `GATEWAYS` is a `frozendict`: a `Mapping`, not a `dict`, and item assignment raises.

Generics and callbacks.

- `Quoter[T: Consignment]` has its variance inferred. A general quoter serves hazmat consignments,
  the reverse is `[arg-type]` and fails at runtime with `AttributeError`.
- `PricingRule.__call__(self, consignment, /)` accepts functions whatever their parameter name.
  Without `/` the names must match and mypy reports `[assignment]`.

Protocol or ABC.

- An ABC refuses an incomplete subclass at construction (runtime and `[abstract]`) and shares
  `reference()`. The Protocol is compared where the value is passed.
- `AircoGateway` inherits `CarrierBase` and satisfies `CarrierGateway` by shape.
- Subclassing a Protocol explicitly makes the class nominal: mypy says `[abstract]`, the runtime
  instantiates it and the inherited `...` body returns `None`.
- `typing.override` catches a misspelled override.
- mypy 2.4.1 gives no "missing protocol member" note when the single required member is wholly
  absent; a conflicting member is explained.

`runtime_checkable`.

- It checks names only: a wrong signature and a non-callable attribute still pass `isinstance`.
- A data protocol refuses `issubclass`.
- On 3.15 a sub-protocol without its own decorator warns on `isinstance` and will raise in 3.20.

## Layout

- `src/structural_typing/domain.py`: `ConsignmentId`, `Weight`, `Money`, `Consignment`,
  `HazmatConsignment`, `BookingError`.
- `src/structural_typing/carriers.py`: `CarrierGateway`, `FastlineGateway`, `CarrierBase`,
  `AircoGateway`, `GATEWAYS`, `find_gateway`, `book_with`, `ACCOUNT_DEFAULT`, `carriers_to_ask`.
- `src/structural_typing/pricing.py`: `PricingRule`, `flat_rate`, `per_kg`, `no_discount`, `quote`,
  `Quoter`, `GeneralQuoter`, `HazmatQuoter`, `price_all`, `price_hazmat`.

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

`tests/test_absence.py`

- `test_find_gateway_returns_none_for_an_unknown_code`: an unknown code gives `None`, a known one a gateway.
- `test_book_with_turns_absence_into_a_booking_error`: a known carrier books, an unknown one raises `BookingError`.
- `test_a_null_gateway_hides_a_lost_booking`: the do-nothing gateway returns `""` and nothing raises.
- `test_no_discount_is_a_null_object_that_loses_nothing`: the default discount changes nothing and a real one subtracts.
- `test_a_sentinel_separates_not_given_from_none`: three branches, an unknown code, copy identity and truthiness.
- `test_the_registry_is_a_frozendict`: item assignment raises and the registry is not a `dict`.

`tests/test_generics.py`

- `test_a_general_quoter_serves_hazmat_consignments`: a quoter of the general type prices both kinds.
- `test_a_hazmat_quoter_fails_on_a_general_consignment_at_runtime`: `AttributeError` naming `un_number`.
- `test_hazmat_quoter_surcharge_follows_the_un_number`: a listed and an unlisted UN number.
- `test_hazmat_consignment_validates_its_un_number`: four malformed numbers raise `ValueError`.
- `test_callback_protocol_accepts_any_parameter_name`: `flat_rate` and `per_kg` both price.

`tests/test_disambiguate.py`

- `test_abc_refuses_an_incomplete_subclass_at_construction`: `TypeError` naming `book`.
- `test_both_carriers_satisfy_the_protocol_one_by_inheritance`: one carrier by shape, one by inheritance.
- `test_airco_marks_its_book_as_an_override`: the `__override__` marker is set.
- `test_explicit_protocol_subclass_is_nominal_and_still_instantiable`: the inherited body returns `None`.

`tests/test_runtime_checkable.py`

- `test_runtime_checkable_checks_names_only`: a wrong signature and an attribute pass `isinstance`.
- `test_a_data_protocol_refuses_issubclass`: `TypeError` naming the non-method member.
- `test_an_undecorated_subprotocol_warns_on_isinstance`: `DeprecationWarning`, caught with `pytest.warns`.

`tests/test_domain.py`

- `test_weight_must_be_positive_and_finite`: zero, negative, infinite and NaN raise `ValueError`.
- `test_money_addition_needs_one_currency`: mixed currencies raise `ValueError`.

`tests/test_static.py`

- `test_mypy_requires_a_branch_for_absence`: unguarded is `[union-attr]`; four narrowing forms are clean.
- `test_mypy_requires_a_branch_for_the_sentinel`: `[union-attr]` for `None` and for the sentinel, then clean.
- `test_mypy_infers_quoter_variance`: `[arg-type]` one way, clean the other.
- `test_mypy_matches_callback_parameter_names_without_slash`: `[assignment]` without `/`, clean with it.
- `test_mypy_checks_protocols_at_use_and_abcs_at_construction`: `[assignment]`, `[abstract]` twice and `[misc]` for a misspelled override.
- `test_mypy_explains_a_conflicting_member_but_not_a_wholly_absent_one`: the note appears for a conflict only.
- `test_mypy_accepts_a_null_gateway`: the do-nothing gateway is clean.

Classes named with a leading underscore in the test modules are negative fixtures and are not
part of the model code.
