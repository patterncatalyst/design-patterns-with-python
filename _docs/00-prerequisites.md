---
title: "Prerequisites and the toolchain"
order: 0
layout: tutorial
sectionid: docs
part: "orientation"
description: "The Python 3.15, uv, ruff, mypy and pytest toolchain on Fedora, and a consignment example that checks it works."
---

## Learning objectives

By the end of this chapter you can:

- Install uv and a pinned CPython 3.15 on Fedora without containers and without touching system Python.
- Create the single locked environment for the whole repository with one `uv sync` from the root.
- Run `scripts/check-prereqs.sh` and read its table.
- Run the four gates (ruff check, ruff format, `mypy --strict`, pytest) for one example or for all of them.
- Read the consignment value objects in `examples/00-prerequisites`.
- Point VS Code or PyCharm at the project interpreter, and remove everything you installed.

## Why this matters

Every example is a small Python package with its own tests. A run on your machine has to resolve the same interpreter, the same dependency versions and the same checks as CI, so a green local run predicts a green pull request. Everything is local: the reference platform is Fedora 44, with no Docker, Podman, virtual machine or cloud account.

A misspelled attribute or a `None` passed where a value is required fails only when that line runs. `mypy --strict` as a build gate moves that failure to before the merge. A `Protocol`, an optional value or a frozen dataclass is useful only when a tool rejects code that breaks it.

## The toolchain and its pins

uv manages the interpreter, the virtual environment, dependency resolution and the lockfile, so there's no separate `pyenv`, `venv`, `pip` or `pip-tools`. ruff lints and formats in one binary, in place of flake8, isort and black. mypy checks types, pytest runs the tests, and pytest-mock supplies the `mocker` fixture.

| Tool | Version | Role |
| --- | --- | --- |
| CPython | 3.15.2 | Interpreter, installed by uv |
| uv | 0.13.7 | Interpreter, environment, lockfile |
| pytest | 9.2.0 | Test runner |
| pytest-mock | 3.17.0 | `mocker` fixture over `unittest.mock` |
| ruff | 0.17.4 | Lint and format |
| mypy | 2.4.1 | Static types, run with `--strict` |

Verified 2026-11-05; re-verified before each release. The pins live in three files:

- `.python-version` holds `3.15.2`, which uv reads to pick the interpreter.
- The root `pyproject.toml` pins the four Python packages with exact `==` in one `dev` dependency group.
- `uv.lock` records the full resolution with hashes.

Examples carry no tool configuration of their own, so the root `[tool.ruff]`, `[tool.mypy]` and `[tool.pytest.ini_options]` tables apply everywhere: strict mode, a 100-column line and the same lint rules in every example.

{% include excalidraw.html name="00-prerequisites" described="true" caption="Figure 0.1: The local build-and-test loop. One locked environment feeds lint, format, strict type checking and tests in order; a red step returns you to the source, and the prerequisites script gates the toolchain first." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-00-prerequisites" markdown="1">
From the top: "Edit the source" (`src/consignments/consignment.py`) leads to `uv sync --locked --all-packages` (one interpreter, one lockfile, one `.venv`), with `scripts/check-prereqs.sh` beside it, gating the toolchain first. Below the sync come `ruff check, ruff format --check`, then `mypy --strict src tests`, then `pytest`, and at the bottom "green", ready to build on. A dashed "red" box beside the three gates sends a failure back to fixing the source and rerunning.
</div>
</details>

The prerequisites script runs once. After that, each edit passes the four gates in order, and none needs a network after the first sync.

## Installing on Fedora

Install uv, then let uv install the interpreter. Use the official installer, which puts `uv` in `~/.local/bin`, or the Fedora package:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or: sudo dnf install uv
uv python install 3.15.2
```

uv puts a standalone CPython build in its own directory under your home. It doesn't replace the system `python3` that Fedora's tools depend on, and it needs no root. It does link `~/.local/bin/python3.15`, which can shadow a system `python3.15` earlier on `PATH`. Open a new shell and confirm with `uv --version`.

## Cloning and the one-time sync

```bash
git clone https://github.com/patterncatalyst/design-patterns-with-python.git
cd design-patterns-with-python
uv sync --locked --all-packages
```

The repository is a uv workspace. The root `pyproject.toml` is virtual, meaning it isn't a package itself, and every directory under `examples/` is a member with its own `src/` layout. `uv sync` builds one `.venv` at the root and installs every member into it in editable mode.

| Flag or choice | Why |
| --- | --- |
| `--locked` | Fails if `uv.lock` is out of date instead of re-resolving, so your environment matches CI's. |
| `--all-packages` | A plain `uv sync --locked` from the root installs the dev tools but removes every member, so tests can't import their package. |
| Run from the root | Inside a member before the root sync, uv treats the member as the project and installs no pytest or mypy. |

After that one sync, a plain `uv run` from any member directory reuses the environment.

## Checking the machine

```bash
bash scripts/check-prereqs.sh
```

The script installs nothing. It confirms that uv is on `PATH`, that a 3.15 interpreter resolves, that git exists, and that ruff, mypy and pytest run from `.venv`. Before the sync those three rows fail with a hint to run `uv sync --locked --all-packages`. It prints a table, exits non-zero if any row fails (printing the uv install command), and always ends with the teardown command. Run it first when something behaves oddly.

## The four gates

Every example passes four checks, in this order:

1. `uv run ruff check .`: pycodestyle, pyflakes, import order, pyupgrade, bugbear, simplify, ruff's `RUF` rules, and the pytest-style and naming sets.
2. `uv run ruff format --check .`: the code is already formatted.
3. `uv run mypy --strict src tests`: types, with unreachable code and redundant casts reported.
4. `uv run pytest`: behaviour.

`bash scripts/verify.sh` runs them across the repository after the locked sync, with a strict type check of the repository's scripts before the tests. It stops at the first failure and ends with `verify: all steps passed`. CI runs the same command, so run it before opening a pull request.

Each gate catches defects the others accept:

| Gate | Catches |
| --- | --- |
| ruff check | An unused import, a mutable default argument, a bare `except` |
| ruff format | Layout arguments in review |
| mypy | A wrong argument type, a missing attribute, a `None` reaching a call that needs a value |
| pytest | Well-typed but wrong behaviour: a hash that disagrees with equality, an off-by-one validator |

A type checker can't know that `"CN-1"` is too short, and a test suite proves an annotation correct only on the lines it runs.

## Running one example or all of them

From an example directory, `uv run pytest` and `uv run mypy --strict src tests` use the shared root environment and the root configuration: pytest, ruff and mypy each walk up to the first `pyproject.toml` that defines their settings. From the root, `uv run pytest` collects every example, and the ruff commands take a path such as `examples/00-prerequisites`.

mypy is the exception. Examples keep their tests in a `tests/` directory without `__init__.py`, so two examples whose test files share a name give mypy two modules with one name, and it stops with a duplicate-module error. pytest avoids this with `--import-mode=importlib` in the root configuration; mypy has no equivalent. Run mypy once per example from inside it, as `verify.sh` does in a loop. Adding `__init__.py` to every `tests/` would also work, but it changes import behaviour in ways that complicate the examples.

## The example: a consignment

The example is a consignment with an identifier, two ports and a weight, in `examples/00-prerequisites/src/consignments/consignment.py`. Identifiers and weights are value objects: frozen, slotted dataclasses that validate themselves on construction.

```python
@dataclass(frozen=True, slots=True)
class ConsignmentId:
    """A consignment reference such as ``CN-00012345``."""

    value: str

    def __post_init__(self) -> None:
        if not _ID_PATTERN.fullmatch(self.value):
            raise ValueError(f"consignment id must look like CN-12345678, got {self.value!r}")
```

| Option | Effect |
| --- | --- |
| `frozen=True` | Assigning a field raises `FrozenInstanceError`; with the default `eq=True`, a `__hash__` consistent with equality is generated, so instances work as dict keys and set members. |
| `slots=True` | Generates `__slots__`: no per-instance `__dict__`, and undeclared attributes are rejected. |
| `__post_init__` | Runs after the generated `__init__`, so an invalid `ConsignmentId` can't be constructed and no later code checks one. |

`Weight` has the same shape and rejects zero, negative, NaN and infinite values. `Consignment` composes them:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class Consignment:
    """A shipment from an origin port to a destination port."""

    id: ConsignmentId
    origin: str
    destination: str
    weight: Weight

    def reweigh(self, new: Weight) -> Consignment:
        """Return a copy carrying the new weight; this instance is unchanged."""
        return replace(self, weight=new)
```

`kw_only=True` forces every argument to be named, so `Consignment(id=..., origin="NLRTM", destination="SGSIN", weight=...)` can't swap the two string ports the way a positional call could. The class also validates both port codes, five uppercase letters, in its own `__post_init__`, elided here.

A frozen instance can't change its weight by assignment. `dataclasses.replace` calls `__init__` again, so `__post_init__` checks the copy like any new instance, and the original keeps its weight. The annotation `-> Consignment` needs no quotes: since Python 3.14, annotations are evaluated lazily (PEP 649), so a class can name itself in its own signatures.

The behaviour that follows:

- Equality is field by field, with no identity involved; two equal consignments share a hash and collapse to one set member.
- `str()` of a `ConsignmentId` is its bare value, which is what log lines and error messages show.
- Malformed ids, non-positive or non-finite weights and bad port codes raise `ValueError` with a message naming the rule.

## Bumping a pin

1. Survey upstream and read the release notes for any minor-version jump: a new mypy can add strict-mode errors to code that passed yesterday.
2. Edit the exact `==` pin in the root `pyproject.toml`.
3. Run `uv lock`, then `uv sync --locked --all-packages`.
4. Run `bash scripts/verify.sh`, and commit `pyproject.toml` and `uv.lock` together.

Committing one without the other is the usual cause of a `--locked` failure. A new interpreter follows the same path, with `.python-version` to edit and `uv python install` as an extra step.

## Troubleshooting

`bash scripts/check-prereqs.sh` names the failing row for most environment problems.

| Symptom | Cause and fix |
| --- | --- |
| `python --version` prints the system release | You're bypassing the environment. Use `uv run python` or activate `.venv`; check `.python-version` is present. `uv python list` shows what uv sees. |
| `uv sync --locked` says the lockfile needs updating | `pyproject.toml` changed without `uv lock`, or a pin was edited by hand. Run `uv lock`, review the `uv.lock` diff, sync again. Dropping `--locked` hides the problem. |
| Old tool versions after a pin bump | `uv run` re-syncs after `uv lock`; an activated `.venv` or a direct call into `.venv/bin` doesn't. Run `uv sync --locked --all-packages`. |
| mypy reports a duplicate module | It ran from the root over several examples. Run it inside one example. |
| The editor underlines every import | The editor uses the system interpreter. Select `.venv/bin/python` at the repository root. |

## Editors

Use VS Code or PyCharm, with `.venv/bin/python` at the repository root as the interpreter. VS Code needs the Python and Ruff extensions; PyCharm takes the interpreter in its project settings and can run ruff and mypy as external tools. The CLI output of the four gates is authoritative, because CI runs those commands.

## Build, run, observe

From a fresh clone, after the one-time sync, run the prerequisites script. Paths are shown with the checkout replaced by `<repo>`.

```text
$ bash scripts/check-prereqs.sh
Checking local toolchain for Design Patterns with Python

TOOL     STATUS DETAIL
uv       OK     uv 0.13.7 (x86_64-unknown-linux-gnu)
python   OK     Python 3.15.2 (<repo>/.venv/bin/python)
git      OK     git version 2.56.0
ruff     OK     ruff 0.17.4
mypy     OK     mypy 2.4.1 (compiled: yes)
pytest   OK     pytest 9.2.0

All prerequisites found.
Teardown: rm -rf .venv && uv cache clean
```

Then run the consignment example from its directory:

```text
$ cd examples/00-prerequisites
$ uv run pytest
============================= test session starts ==============================
platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collected 26 items

tests/test_consignment.py ..........................                     [100%]

============================== 26 passed in 0.03s ==============================
$ uv run mypy --strict src tests
Success: no issues found in 3 source files
```

All 26 cases pass, and mypy checks the module, the package `__init__` and the tests. `rootdir` and `configfile` show that pytest found the root `pyproject.toml` from inside `examples/00-prerequisites`.

- **Break the annotation.** Change `reweigh` to return `str`. mypy reports four errors in two files: `[return-value]` at that line, and two `[attr-defined]` and one `[comparison-overlap]` in the tests. pytest still passes all 26, because nothing at runtime reads the annotation.

Finally, `bash scripts/verify.sh` from the root runs every gate for every example.

## Teardown

| Remove | Command |
| --- | --- |
| The environment | `rm -rf .venv` |
| uv's download and build cache | `uv cache clean` |
| The interpreter, if nothing else uses it | `uv python uninstall 3.15.2` |
| uv, installer route | `rm ~/.local/bin/uv ~/.local/bin/uvx` |
| uv, package route | `sudo dnf remove uv` |

Nothing else on the system changes.

## What you can do now

- Install uv and a pinned CPython without containers, using the installer and `.python-version`, leaving system Python alone.
- Build the one locked environment with `uv sync --locked --all-packages` from the root.
- Read the `scripts/check-prereqs.sh` table and fix the failing row.
- Run ruff check, ruff format, `mypy --strict` per member and pytest, or all of them with `bash scripts/verify.sh`.
- Write a validating value object like `ConsignmentId`, `Weight` and `Consignment`, and see mypy and pytest disagree over `reweigh`.
- Point an editor at `.venv/bin/python` and undo the install with the teardown commands.

## For deeper coverage

- [uv documentation](https://docs.astral.sh/uv/): projects, workspaces, lockfiles, and Python version management.
- [pytest documentation](https://docs.pytest.org/en/stable/): fixtures, parametrisation, and configuration discovery.
- [mypy documentation](https://mypy.readthedocs.io/en/stable/): the strict flag set and per-module configuration.
- [ruff documentation](https://docs.astral.sh/ruff/): rule sets, formatter behaviour, and configuration.
- [PEP 557, Data Classes](https://peps.python.org/pep-0557/): the original specification of `@dataclass`, including `__post_init__` and `replace`.
- [The bibliography]({{ '/bibliography/' | relative_url }}): Luciano Ramalho's *Fluent Python* covers dataclasses and the data model in depth, and Brett Slatkin's *Effective Python* is the companion for everyday idiom.
- [dataclasses in the standard library](https://docs.python.org/3.15/library/dataclasses.html): `frozen`, `slots`, and `kw_only` as they work in 3.15.
