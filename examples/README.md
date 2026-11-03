# Examples

Each example is a self-contained Python package with its own `pyproject.toml`,
a `src/` layout and a `tests/` directory. All examples are members of a single uv
workspace rooted at the repository top level, so they share one lockfile, one virtual
environment and one set of tool versions (Python 3.14, pytest, pytest-mock, ruff, mypy).

## Layout

```
examples/<name>/
  pyproject.toml
  src/<package>/      the code the chapter discusses
  tests/              pytest tests for it
```

Lint, format, type-check and test settings live once, in the root `pyproject.toml`.
Examples do not repeat them.

## Setup

Install [uv](https://docs.astral.sh/uv/), then once from the repository root:

```bash
uv sync --locked --all-packages
```

This creates `.venv` and installs the pinned tools and every example.

## Running everything from the root

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
for d in examples/*/; do (cd "$d" && uv run mypy --strict src tests); done
```

mypy runs once per example because different examples may reuse the same test file
names, which a single mypy invocation rejects as duplicate modules. pytest handles this
with its `importlib` import mode.

## Running one example

```bash
cd examples/<name>
uv run pytest
uv run mypy --strict src tests
```

Run the setup step above first. Without it, `uv run` inside an example installs only
that example and the shared tools are missing.
