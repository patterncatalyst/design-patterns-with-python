# Prerequisites smoke test

A small shipping model that exercises the whole toolchain: uv, Python 3.15, ruff,
mypy in strict mode and pytest. If the commands below pass, the environment is ready
for the other examples.

## The model

`src/consignments/consignment.py` defines three immutable value types:

- `ConsignmentId`: a reference of the form `CN-` followed by eight digits.
- `Weight`: a mass in kilograms, finite and greater than zero.
- `Consignment`: an id, an origin and destination port code (five uppercase letters,
  as in a UN/LOCODE) and a weight. `reweigh` returns an amended copy built with
  `dataclasses.replace`.

All three are frozen, slotted dataclasses. Each validates in `__post_init__` and raises
`ValueError` on bad input, so an invalid instance cannot exist.

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

From the repository root, lint and format checks for this example:

```bash
uv run ruff check examples/00-prerequisites
uv run ruff format --check examples/00-prerequisites
```

## What the tests verify

`tests/test_consignment.py`:

- Equal values compare equal, and a different weight compares unequal.
- Equal consignments hash alike, so they work as dict keys and set members.
- `reweigh` returns a new consignment with the new weight and leaves the original as it was.
- `dataclasses.replace` changes one field and keeps the rest.
- Assigning to a field raises `dataclasses.FrozenInstanceError`.
- `ConsignmentId` renders as its string value.
- Malformed ids (wrong prefix, case, or digit count) raise `ValueError`.
- Zero, negative, NaN and infinite weights raise `ValueError`.
- Origin and destination codes that are not five uppercase letters raise `ValueError`.
