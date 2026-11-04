---
title: "Prerequisites and the toolchain"
order: 0
layout: tutorial
sectionid: docs
part: "orientation"
description: "The Python 3.15, uv, ruff, mypy, and pytest toolchain this book builds against on Fedora, and the consignment smoke-test example that proves it works."
---

## Learning objectives

By the end of this chapter you can:

- Install uv and a pinned CPython 3.15 on Fedora without containers and without touching system Python.
- Create the single locked environment for the whole repository with one `uv sync` and explain why it runs once, from the root.
- Run `scripts/check-prereqs.sh` and read its table.
- Name the four verification gates (ruff check, ruff format, `mypy --strict`, pytest) and run them for one example or for all of them.
- Read the consignment model in `examples/00-prerequisites` and say what each of its tests proves.
- Point VS Code or PyCharm at the project interpreter and remove everything this chapter installed.

## Why this matters

Every example in this book is a small Python package with its own tests, and every chapter ends by running it. That only works if the reader's machine and the author's machine resolve to the same interpreter, the same dependency versions, and the same checks. The toolchain here is local only. The reference platform is Fedora 44, and nothing in the book asks for Docker, Podman, a virtual machine, or a cloud account. What you install in this chapter is what CI installs, so a green run on your machine predicts a green pull request.

A misspelled attribute or a `None` passed where a value is required fails only when that line runs. `mypy --strict` as a build gate moves that failure to before the merge. The patterns in later chapters lean on this: a `Protocol`, an optional value, or a frozen dataclass is useful only when a tool rejects code that breaks it.

## The toolchain and its pins

Five tools on one interpreter do all the work, and uv installs or drives each of them. uv is the single entry point for interpreter management, virtual environments, dependency resolution, and the lockfile, so there is no separate `pyenv`, `venv`, `pip`, or `pip-tools` step to learn. ruff covers linting and formatting in one binary, replacing the usual flake8, isort, and black trio. mypy checks types. pytest runs the tests, and pytest-mock supplies the `mocker` fixture for the chapters that need a test double.

| Tool | Version | Role |
| --- | --- | --- |
| CPython | 3.15.2 | Interpreter, installed by uv |
| uv | 0.13.7 | Interpreter, environment, lockfile |
| pytest | 9.2.0 | Test runner |
| pytest-mock | 3.17.0 | `mocker` fixture over `unittest.mock` |
| ruff | 0.17.3 | Lint and format |
| mypy | 2.4.1 | Static types, run with `--strict` |

Verified 2026-11-04; re-verified before each release. The pins live in three places. `.python-version` holds `3.15.2`, which uv reads to pick the interpreter. The root `pyproject.toml` lists the four Python packages as exact `==` pins in a single `dev` dependency group, and `uv.lock` records the full resolution with hashes. Members of the repository carry no tool configuration of their own, so the root `[tool.ruff]`, `[tool.mypy]`, and `[tool.pytest.ini_options]` tables apply to every example. Strict mode, a 100-column line, and the selected lint rules are therefore identical everywhere.

{% include excalidraw.html name="00-prerequisites" caption="Figure 0.1: The local build-and-test loop. One locked environment feeds lint, format, strict type checking and tests in order; a red step returns you to the source, and the prerequisites script gates the toolchain first." %}

The prerequisites script runs once. After that, each edit passes through the same four gates in the order shown, and none of them needs a network after the first sync.

## Installing on Fedora

Install uv, then let uv install the interpreter. The first line uses the official installer, which places `uv` in `~/.local/bin`; the commented alternative installs the Fedora package instead. Use one or the other.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or: sudo dnf install uv
uv python install 3.15.2
```

uv downloads a standalone CPython build into its own directory under your home. It doesn't replace the system `python3`, which Fedora's own tools depend on, and it needs no `dnf` package or root. It does link `~/.local/bin/python3.15`, which can shadow a system `python3.15` earlier on `PATH`. Open a new shell so `~/.local/bin` is on `PATH`, then confirm with `uv --version`.

## Cloning and the one-time sync

```bash
git clone https://github.com/patterncatalyst/design-patterns-with-python.git
cd design-patterns-with-python
uv sync --locked --all-packages
```

The repository is a uv workspace. The root `pyproject.toml` is virtual, meaning it is not a package itself, and every directory under `examples/` is a member with its own `src/` layout. `uv sync` builds one `.venv` at the root and installs every member into it in editable mode. `--locked` fails the command if `uv.lock` is out of date instead of silently re-resolving, which keeps your environment identical to CI's. The sync runs once because every later command reuses the result. `--all-packages` matters because the dev tools belong to the root, not to a member: inside a member directory uv treats the member as the project and wouldn't install pytest or mypy. Syncing all packages from the root installs everything once, and a plain `uv run` from any member directory then reuses that environment.

## Checking the machine

```bash
bash scripts/check-prereqs.sh
```

The script installs nothing and creates no environment. It confirms that uv is on `PATH`, that a 3.15 interpreter resolves, that git exists, and that ruff, mypy and pytest run from the existing `.venv`; before the sync those three rows fail with a hint to run `uv sync --locked --all-packages`. It prints a table and exits non-zero if any row fails. If one does, it also prints the uv install command, and it always ends with the teardown command. Run it first when something behaves oddly: most environment problems show up as one failing row.

## The four gates

Every example must pass four checks, in this order:

1. `uv run ruff check .` for lint rules: pycodestyle, pyflakes, import order, pyupgrade, bugbear, simplify, ruff's own `RUF` rules, and the pytest-style and naming sets.
2. `uv run ruff format --check .` to confirm the code is already formatted.
3. `uv run mypy --strict src tests` for types, with unreachable code and redundant casts also reported.
4. `uv run pytest` for behaviour.

`bash scripts/verify.sh` runs all of them across the repository, preceded by the locked sync, with a strict type check of the repository's own scripts before the tests. It stops at the first failure and prints `verify: all steps passed` at the end. This is the command to run before opening a pull request, and it is what CI runs.

## Running one example or all of them

Each example is also runnable by itself. From an example directory, `uv run pytest` and `uv run mypy --strict src tests` use the shared root environment and the root configuration, because pytest, ruff and mypy each walk up from the current directory to the first `pyproject.toml` that defines their settings. From the root, `uv run pytest` collects every example, and the ruff commands take a path such as `examples/00-prerequisites`.

mypy is the exception to "run it from the root". Examples keep their tests in a `tests/` directory without `__init__.py`, so two examples that both contain `tests/test_model.py` would give mypy two modules called `test_model` and it would stop with a duplicate-module error. pytest avoids the problem through `--import-mode=importlib` in the root configuration, but mypy has no equivalent. The answer is to run mypy once per example, from inside it, which is what `verify.sh` does in a loop. Adding `__init__.py` to every `tests/` directory would also work, but it changes import behaviour in ways that complicate the examples, so the layout stays minimal.

## The example: a consignment

The shipping domain runs through the whole book, and this chapter's example is its smallest piece: a consignment with an identifier, two ports, and a weight. The whole model is in `examples/00-prerequisites/src/consignments/consignment.py`. Identifiers and weights are value objects, written as frozen, slotted dataclasses that validate themselves on construction.

```python
@dataclass(frozen=True, slots=True)
class ConsignmentId:
    """A consignment reference such as ``CN-00012345``."""

    value: str

    def __post_init__(self) -> None:
        if not _ID_PATTERN.fullmatch(self.value):
            raise ValueError(f"consignment id must look like CN-12345678, got {self.value!r}")
```

Three options on the decorator do separate jobs. `frozen=True` makes assignment to a field raise `FrozenInstanceError` and, together with the default `eq=True`, generates a `__hash__` consistent with equality, so instances work as dictionary keys and set members. `slots=True` generates `__slots__`, which removes the per-instance `__dict__` and rejects attributes that weren't declared. `__post_init__` runs after the generated `__init__`, which makes it the place for validation: an invalid `ConsignmentId` can't be constructed, so no later code needs to check one. `Weight` follows the same shape and rejects zero, negative, NaN, and infinite values.

`Consignment` composes them:

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

`kw_only=True` forces every argument to be named at the call site. With two string fields of the same type in a row, `Consignment(id=..., origin="NLRTM", destination="SGSIN", weight=...)` can't silently swap the ports the way a positional call could. The class body also validates both port codes in its own `__post_init__`, elided here. Since the instance is frozen, a change to weight can't be an assignment. `reweigh` calls `dataclasses.replace`, which builds a new instance from the old one with one field changed. It calls `__init__` again, so `__post_init__` checks the copy (the port codes) like any new instance; the `Weight` was validated when it was built. The method annotation `-> Consignment` needs no quotes: since Python 3.14, annotations are evaluated lazily (PEP 649), so a class can name itself in its own signatures.

## What the tests prove

`tests/test_consignment.py` holds six behaviour tests and three parametrised groups, which pytest expands to 26 cases. Each group covers one validation rule.

- Equal values compare equal, and a consignment with a different weight doesn't. Dataclass equality is field by field, with no identity involved.
- Two equal consignments have the same hash, collapse to one member of a set, and find each other as dictionary keys. This is the observable result of `frozen=True` with `eq=True`.
- `reweigh` returns a different object with the new weight and the same id, and the original keeps its weight.
- `dataclasses.replace` can change any single field, here the destination, and leaves the others alone.
- `str()` of a `ConsignmentId` is its bare value, which is what log lines and error messages show.
- Assigning to a field raises `FrozenInstanceError`. The one `# type: ignore[misc]` in the file marks the line where mypy itself reports the illegal assignment; the test then proves the runtime agrees.
- Malformed ids, non-positive or non-finite weights, and port codes that are not five uppercase letters raise `ValueError` with the expected message, for both origin and destination. The `match=` argument ties each case to the specific rule, so a test can't pass by failing for an unrelated reason.

## What each gate catches

The gates overlap less than they seem to. ruff check finds an unused import, a mutable default argument, or a bare `except` before anything runs, and ruff format settles layout so reviews don't argue about it. mypy finds the wrong argument type, the attribute that doesn't exist, and the `None` that reaches a call expecting a value, none of which a passing test proves absent unless a test happens to hit that line. pytest finds behaviour that is well typed and wrong: a hash that disagrees with equality, a validator with an off-by-one. The `reweigh` experiment in Build, run, observe shows the asymmetry in one direction, and a test that passes a malformed id shows it in the other, since a type checker can't know that `"CN-1"` is too short. Skipping any one gate leaves a class of defect that the other three accept.

## Bumping a pin

Pins move in the same order every time. Survey upstream first and read the release notes of anything with a minor-version jump, because a new mypy release can add strict-mode errors to code that passed yesterday. Then edit the exact `==` pin in the root `pyproject.toml`, run `uv lock` to record the new resolution and hashes, and run `uv sync --locked --all-packages` to install it. Finish with `bash scripts/verify.sh` and commit `pyproject.toml` and `uv.lock` together. A change to one without the other is the usual cause of the `--locked` failure described below. A new interpreter follows the same path, with `.python-version` as the file to edit and `uv python install` as the extra step.

## Troubleshooting

Most failures come from the environment, not the code, and `bash scripts/check-prereqs.sh` names the failing row. The common ones:

- **The wrong Python is picked up.** If `python --version` prints the system 3.x release, you're bypassing the environment. Use `uv run python` or activate `.venv`, and check that `.python-version` is present in the checkout. `uv python list` shows what uv can see.
- **`uv sync --locked` refuses to run.** The message says the lockfile needs updating. Either `pyproject.toml` changed without a matching `uv lock`, or you edited a pin by hand. Run `uv lock`, review the diff to `uv.lock`, and sync again. Dropping `--locked` hides the problem rather than fixing it.
- **Tools report the old versions after a pin bump.** `uv run` re-syncs the environment after `uv lock` on its own. An activated `.venv`, or a direct call to a tool in `.venv/bin`, doesn't, so run `uv sync --locked --all-packages` after `uv lock`.
- **mypy reports a duplicate module.** It was run once from the root over several examples. Run it from inside one example, as `verify.sh` does.
- **The editor underlines every import.** The editor is using the system interpreter. Select `.venv/bin/python` at the repository root, as described next.

## Editors

VS Code and PyCharm both work, and the book never asks for an editor-only action. In either one, select `.venv/bin/python` at the repository root as the interpreter. VS Code needs the Python and Ruff extensions; PyCharm takes the interpreter through its project settings and can run ruff and mypy as external tools. Whatever the editor highlights, the authoritative result is the CLI output of the four gates, because those are the commands CI runs.

## Build, run, observe

From a fresh clone, after the one-time sync, run the prerequisites script. Paths are shown with the checkout replaced by `<repo>`.

```text
$ bash scripts/check-prereqs.sh
Checking local toolchain for Design Patterns with Python

TOOL     STATUS DETAIL
uv       OK     uv 0.13.7 (x86_64-unknown-linux-gnu)
python   OK     Python 3.14.10 (<repo>/.venv/bin/python)
git      OK     git version 2.56.0
ruff     OK     ruff 0.17.3
mypy     OK     mypy 2.4.1 (compiled: yes)
pytest   OK     pytest 9.2.0

All prerequisites found.
Teardown: rm -rf .venv && uv cache clean
```

Then run the example's tests from its directory.

```text
$ cd examples/00-prerequisites
$ uv run pytest -v
============================= test session starts ==============================
platform linux -- Python 3.14.10, pytest-9.2.0, pluggy-1.7.0 -- <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 26 items

tests/test_consignment.py::test_equal_values_compare_equal PASSED        [  3%]
tests/test_consignment.py::test_consignment_is_usable_as_dict_key_and_set_member PASSED [  7%]
tests/test_consignment.py::test_reweigh_returns_new_consignment_and_leaves_original_unchanged PASSED [ 11%]
...
tests/test_consignment.py::test_invalid_port_code_is_rejected[destination-NL1TM] PASSED [100%]

============================== 26 passed in 0.03s ==============================
```

Note `rootdir` and `configfile`: pytest found the root `pyproject.toml` from inside the example, which is the configuration discovery described above.

```text
$ uv run mypy --strict src tests
Success: no issues found in 3 source files
```

Three files are checked: the module, the package `__init__`, and the test file. To see the gate refuse something, change the annotation of `reweigh` to return `str` and rerun. mypy reports four errors in two files: the `[return-value]` error at that line, plus three in the tests (two `[attr-defined]` and one `[comparison-overlap]`). pytest still passes all 26 tests, because nothing at runtime depends on the annotation. That gap is the reason the type check is a separate gate. Finally, run `bash scripts/verify.sh` from the root to execute every gate for every example in one pass.

## Teardown

Everything installed lives in four places. `rm -rf .venv` removes the environment, `uv cache clean` empties uv's download and build cache, and `uv python uninstall 3.15.2` removes the interpreter if no other project of yours uses it. Removing uv itself is `rm ~/.local/bin/uv ~/.local/bin/uvx` for the installer route, or `sudo dnf remove uv` for the package. Nothing else on the system changes.

## For deeper coverage

- [uv documentation](https://docs.astral.sh/uv/): projects, workspaces, lockfiles, and Python version management.
- [pytest documentation](https://docs.pytest.org/): fixtures, parametrisation, and configuration discovery.
- [mypy documentation](https://mypy.readthedocs.io/): the strict flag set and per-module configuration.
- [ruff documentation](https://docs.astral.sh/ruff/): rule sets, formatter behaviour, and configuration.
- [PEP 557, Data Classes](https://peps.python.org/pep-0557/): the original specification of `@dataclass`, including `__post_init__` and `replace`.
- [The bibliography]({{ '/bibliography/' | relative_url }}): Luciano Ramalho's *Fluent Python* covers dataclasses and the data model in depth, and Brett Slatkin's *Effective Python* is the companion for everyday idiom.
- [dataclasses in the standard library](https://docs.python.org/3/library/dataclasses.html): `frozen`, `slots`, and `kw_only` as they work in 3.15.
