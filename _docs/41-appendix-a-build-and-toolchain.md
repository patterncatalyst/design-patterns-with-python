---
title: "Build and toolchain reference: uv, ruff, mypy"
order: 41
layout: tutorial
sectionid: docs
part: "appendices"
appendix: "A"
description: "Reference for the uv, ruff and mypy commands the book uses, the one root configuration each tool reads, and the traps between them."
---

## Learning objectives

By the end of this appendix you can:

- Find the uv, ruff or mypy command for a task and say what it does on the pinned versions.
- Say which file each tool reads, and why a member carries no tool table.
- Build and use the free-threaded environment from the same lockfile.
- Add a member and bump a pin without breaking `--locked`.

## Why this matters

Three tools find their settings by three rules, and the book gives all three one file. mypy discovers its configuration by walking up the file system, and its configuration page is blunt about what follows: "there is no merging of configuration files" ([mypy configuration file](https://mypy.readthedocs.io/en/stable/config_file.html)). Ruff uses the closest configuration file for each file it checks, and "Ruff does not merge settings across configuration files" ([ruff configuration](https://docs.astral.sh/ruff/configuration/)). pytest takes the first file it finds as well, and [pytest reference]({{ '/docs/42-appendix-b-pytest/' | relative_url }}) holds the test for that rule.

A tool table in a member's `pyproject.toml` therefore replaces the root's for that member and doesn't add to it. In recorded runs, a member table with `strict = false` let an unannotated function through mypy, a member `line-length = 120` let a 108-column line through ruff, and a member `addopts = ""` let a `DeprecationWarning` through pytest, each of which the root configuration refuses. Members carry no `[tool.*]` table for that reason. Without a member table, the root file is the one all three tools find from a member directory: ruff reported it as its settings path and pytest as its `configfile`, and mypy applied its strict settings with no flag.

This page is the reference for the commands those files drive. The install, sync and gate walkthrough, and the version table, are in [Prerequisites and the toolchain]({{ '/docs/00-prerequisites/' | relative_url }}) and aren't repeated. The page describes uv 0.13.7, ruff 0.17.4 and mypy 2.4.1. The uv and ruff documentation carries no version, so the flags and counts below come from recorded runs of the pinned binaries, and the documentation is quoted for what it says in general.

## uv: interpreter, environment and lockfile

| Command | What it does here |
| --- | --- |
| `uv python install 3.15.2` | Installs the pinned interpreter into uv's store, or reports that it is already installed. |
| `uv python install 3.15.2t` | Installs the free-threaded build beside it. |
| `uv python list --only-installed` | Lists the interpreters in the store; the free-threaded build appears as `cpython-3.15.2+freethreaded-linux-x86_64-gnu`. |
| `uv sync --locked --all-packages` | Builds the root `.venv` with the dev tools and every member, and fails if `uv.lock` would change. |
| `uv lock` | Rewrites `uv.lock` after a pin or member change. |
| `uv lock --check` | Exits 0 when `uv.lock` is current and 1 when it needs an update. |
| `uv run <command>` | Runs a command in the root environment from the root or from a member directory, without removing anything from it. |
| `uv run --locked <command>` | The same, and fails if `uv.lock` would change; the book-check jobs in CI use it. |

A workspace shares one lockfile: the uv documentation says "the workspace shares a single lockfile, ensuring that the workspace operates with a consistent set of dependencies" ([workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)). The root `pyproject.toml` is virtual. Its `package = false` keeps uv from building the root itself, which the [project configuration page](https://docs.astral.sh/uv/concepts/projects/config/) describes as forcing "a project package not to be built and installed into the project environment". Its `members` globs cover every directory under `examples/` and one other top-level directory of members, and its default groups name the dev group of pytest, pytest-mock, ruff and mypy.

A sync can remove packages, and which commands do depends on the command. The [sync page](https://docs.astral.sh/uv/concepts/projects/sync/) says that exact syncing, the default for `uv sync`, "means it will remove any packages that are not selected for installation", and that `uv run` is inexact, "ensuring that all required packages are installed but not removing extraneous packages". In a recorded run, `uv sync --locked` from the root without `--all-packages` took the environment from 54 distributions to 13. It removed all 41 members and kept pytest, pytest-mock, mypy, ruff and their dependencies. `uv run --no-sync pytest -q examples/00-prerequisites` then failed collection with `ModuleNotFoundError: No module named 'consignments'`. That's why the book's sync names `--all-packages`.

The order also matters for `uv run` inside a member. Before the root sync, `uv run pytest -q` in a member directory created an environment holding that member alone and stopped with `error: Failed to spawn: pytest`. After the root sync, the same command ran in the root `.venv` and passed, and the distribution count didn't change.

`--locked` and `uv lock --check` refuse a lockfile that no longer matches the pins. With `ruff==0.17.4` edited to `ruff==0.17.3` in the root `pyproject.toml` and `uv.lock` untouched, `uv sync --locked --all-packages` exited 1 with this message. `uv lock --check` and `uv run --locked` exited 1 in the same recorded run, and `uv lock --check` printed the same first line with `--check` in place of `--locked`.

<!-- fmt:off -->
```text
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.

hint: To update the lockfile, run `uv lock`.
```
<!-- fmt:on -->

`--frozen` is the looser option. Its help line reads "Sync without updating the `uv.lock` file", where `--locked` reads "Assert that the `uv.lock` will remain unchanged". The book uses `--locked`, so a stale lockfile stops the command.

A pin bump runs the failure in reverse: once the `==` pin changes, `uv lock` records the new resolution (in the recorded run it printed `Updated ruff v0.17.4 -> v0.17.3`), and [Prerequisites and the toolchain]({{ '/docs/00-prerequisites/' | relative_url }}) gives the full order.

## Adding a member

A member is a directory under `examples/` with its own `pyproject.toml` and `src/` layout. The command is `uv init --lib --vcs none --no-readme --no-description --author-from none --name <project> examples/<slug>`. It creates three files, `pyproject.toml`, `src/<package>/__init__.py` and `py.typed`, and leaves the root `pyproject.toml` byte-identical, because the `examples/*` glob already covers the new directory; uv prints that the project is already a member of the workspace. Two lines need editing to match the repo, `requires-python` from `>=3.15.2` to `>=3.15` and the build requirement from `uv_build>=0.13.7,<0.14.0` to `<0.14`. Then `uv lock` records the member. The result looks like this.

<!-- fmt:off -->
```toml
[project]
name = "pytest-reference"
version = "0.1.0"
requires-python = ">=3.15"
dependencies = []

[build-system]
requires = ["uv_build>=0.13.7,<0.14"]
build-backend = "uv_build"
```
<!-- fmt:on -->

The flags matter. Without them, the same command in a recorded run also wrote a README, the placeholder description `Add your description here`, an `authors` entry holding the git user's name and email and, in a copy with no `.git`, a nested git repository. The directory name `99-init-probe` also gave `module-name = "_99_init_probe"` in a `[tool.uv.build-backend]` table. Chapter directories start with a digit, so `--name` sets the package name and avoids the table.

## The free-threaded environment

CI builds a second environment from the same lockfile and runs the two concurrency examples in it.

<!-- fmt:off -->
```yaml
      - name: Install the free-threaded interpreter
        run: uv python install 3.15.2t
      - name: Build a second environment from the same lockfile
        run: UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15.2t --locked --all-packages
      - name: GIL and asyncio examples on the free-threaded build
        run: .venv-ft/bin/python -m pytest examples/37-the-gil-and-performance examples/38-asyncio-and-the-patterns
```
<!-- fmt:on -->

`UV_PROJECT_ENVIRONMENT` sets the environment's path. The configuration page says "If a relative path is provided, it will be resolved relative to the workspace root", so `.venv-ft` sits beside `.venv`. `--python 3.15.2t` (`-p`, whose help line reads "The Python interpreter to use for the project environment") selects the free-threaded build that `uv python install 3.15.2t` put in the store. Both environments are filled from one `uv.lock`, and `sys._is_gil_enabled()` prints `False` in `.venv-ft/bin/python` and `True` in `.venv/bin/python`. [The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}) covers the two builds.

Ruff needs one line for that directory. Its default exclude list names `.venv` and `venv` but not `.venv-ft`. In a git checkout `.gitignore` lists `.venv-ft/` and ruff's `respect_gitignore` setting is on, so the directory is skipped. In a recorded copy without `.git`, `ruff check .` reported two findings in `.venv-ft/bin/activate_this.py` and `ruff format --check .` reported one file to reformat. With `".venv-ft"` in the root `extend-exclude`, the same copy printed `All checks passed!`.

## ruff: lint and format

The root `select` names ten prefixes from nine linters.

| Prefix | Linter |
| --- | --- |
| `E`, `W` | pycodestyle |
| `F` | Pyflakes |
| `I` | isort |
| `UP` | pyupgrade |
| `B` | flake8-bugbear |
| `SIM` | flake8-simplify |
| `RUF` | Ruff-specific rules |
| `PT` | flake8-pytest-style |
| `N` | pep8-naming |

| Command | What it does here |
| --- | --- |
| `ruff check .` | Lints the repository with the root configuration. |
| `ruff check --fix` | Applies fixes; `--unsafe-fixes` adds those that may not retain the original intent. |
| `ruff check --diff` | Prints the fixes as a diff and writes nothing; it exits 1 when there are diffs. |
| `ruff check --statistics` | Counts findings per rule. |
| `ruff check --output-format concise` | Prints one line per finding. |
| `ruff check --show-settings <file>` | Prints the settings ruff uses for that file, including the `Settings path` of the file it chose. |
| `ruff check --isolated` | Ignores every configuration file. |
| `ruff rule <CODE>` | Prints the rule's page, for example `ruff rule UP045`. |
| `ruff linter` | Lists the linters and their prefixes. |
| `ruff format` | Rewrites files to the formatter's style. |
| `ruff format --check` | Reports files that would change, writes nothing, and exits 1 if any would. |
| `ruff format --diff` | Prints the difference, writes nothing, and exits 1 if there is one. |

To see which file ruff chose for a source file, read the `Settings path` line of `ruff check --show-settings <file>`. From a member directory it named the root `pyproject.toml`, and it named the member's own file once the member had a `[tool.ruff]` table. The root configuration is three tables.

<!-- fmt:off -->
```toml
[tool.ruff]
line-length = 100
target-version = "py315"
extend-exclude = ["_site", ".jekyll-cache", "vendor", ".bundle", ".venv-ft", "scripts/host_ids.py", "scripts/generate_diagram.py"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B", "SIM", "RUF", "PT", "N"]

[tool.ruff.format]
quote-style = "double"
```
<!-- fmt:on -->

Setting `select` replaces ruff's default rule set. The [rules page](https://docs.astral.sh/ruff/rules/) says Ruff enables rules from "the F, E, B, UP, and RUF categories, as well as many more" by default, and the [settings page](https://docs.astral.sh/ruff/settings/) says "Unlike select, which replaces the default rule set when specified, extend-select adds to whatever rules are already active." On ruff 0.17.4, `ruff check --show-settings` lists 407 enabled rules with `--isolated` and 279 with the root configuration. All 279 come from the ten prefixes in the table, and the 407 include linters the root doesn't name, such as `ASYNC`, `FURB`, `PLE`, `PYI` and `S`. The book's selection is the narrower one, and `extend-select` is the setting that would widen it.

The other lines have visible effects. `line-length = 100` is why a 108-column line failed with `E501 Line too long (108 > 100)`. `quote-style = "double"` is the formatter's: `ruff format` rewrote `x = {'a':1}` to `x = {"a": 1}`. `target-version = "py315"` follows the settings page's description, "Ruff will not propose changes using features that are not available in the given version."

A `# noqa: CODE` comment suppresses one code on its line. One that suppresses nothing is itself a finding: `# noqa: B018` on `print(sys.argv)` was reported as `RUF100`, an unused `noqa` directive naming `B018`. `RUF` is in the selection, so the root catches stale suppressions. `--add-noqa` adds such comments to failing lines automatically, and `--ignore-noqa` ignores them; the help lines say so, and the book uses neither.

## mypy: strict types

The [command-line page](https://mypy.readthedocs.io/en/stable/command_line.html) warns that "the exact list of flags enabled by running --strict may change over time". On 2.4.1, `mypy --help` lists thirteen.

| Flag | What it does |
| --- | --- |
| `--disallow-any-generics` | Reports a generic type written without type parameters, such as a bare `list`. |
| `--disallow-subclassing-any` | Reports a class whose base class has type `Any`. |
| `--disallow-untyped-calls` | Reports a call from an annotated function to one without annotations. |
| `--disallow-untyped-defs` | Reports a function definition with no annotations or incomplete ones. |
| `--disallow-incomplete-defs` | Reports a partly annotated function definition. |
| `--check-untyped-defs` | Type checks the bodies of functions that have no annotations. |
| `--disallow-untyped-decorators` | Reports an annotated function decorated with an unannotated decorator. |
| `--warn-redundant-casts` | Reports a `cast` that can be removed. |
| `--warn-unused-ignores` | Reports a `# type: ignore` on a line with no error. |
| `--warn-return-any` | Reports returning a value of type `Any` from a function declared to return something else. |
| `--no-implicit-reexport` | Stops a module re-exporting an import unless it uses `from-as` or `__all__`. |
| `--strict-equality` | Reports comparisons and container checks between types that don't overlap. |
| `--extra-checks` | Adds checks that are correct but may be impractical, such as partial overlap in `TypedDict` updates. |

`--warn-unreachable` isn't in the list. The same page says "the --warn-unreachable flag is not automatically enabled by the strict flag", so the root turns it on. It also repeats `warn_redundant_casts`, which `--strict` already sets: in a recorded run, `--strict` with `--config-file /dev/null` reported `Redundant cast to "int"` with no other flag, and adding `--warn-unreachable` added two `[unreachable]` errors. The repeat is harmless and explicit.

<!-- fmt:off -->
```toml
[tool.mypy]
python_version = "3.15"
strict = true
warn_unreachable = true
warn_redundant_casts = true
```
<!-- fmt:on -->

Most configuration keys mirror a flag: the mypy configuration page says "Most flags correspond closely to command-line flags". `strict = true` is `--strict`, `warn_unreachable = true` is `--warn-unreachable`, and `python_version = "3.15"` is `--python-version`, whose help line reads "Type check code assuming it will be running on Python x.y". An `[[tool.mypy.overrides]]` table in the root sets `ignore_errors = true` for two vendored script modules. The options used in day-to-day runs:

| Option | What it does here |
| --- | --- |
| `--strict` | The thirteen flags above; the book adds it on the command line as well as in the root file. |
| `--warn-unreachable` | Reports code that analysis finds unreachable or redundant. |
| `--config-file FILE` | Uses that file instead of discovery; `/dev/null` replaced the root file and printed `No [mypy] section in config file`. |
| `--enable-error-code NAME` | Turns on one error code. |

Run from a member directory with no flags, mypy still applies the root file: a module with `if isinstance(x, str):` after `x: int = 1` produced two `[unreachable]` errors, and with `--config-file /dev/null` the same module passed. `--no-strict` isn't a flag: mypy refused it as an ambiguous option.

Error codes outside `--strict` exist too. A call to a function decorated with `warnings.deprecated`, imported from another module, passed `mypy --strict`. With `--enable-error-code deprecated` the same call failed with `function m.legacy_rate is deprecated: use quote  [deprecated]`.

The book runs mypy once per member and not once at the root. From the root, a run over the tests of two members stops at a module name they share, and the run exits 2.

<!-- fmt:off -->
```text
examples/39-final-project/tests/conftest.py: error: Duplicate module named "conftest" (also at "examples/38-asyncio-and-the-patterns/tests/conftest.py")
```
<!-- fmt:on -->

Run from its own directory, each of those two members passed `--strict src tests`. mypy's note after the error lists three resolutions: excluding one of the files, adding an `__init__.py`, or using `--explicit-package-bases` or `MYPYPATH`. The book takes none of them and loops over the members instead. `mypy.api.run`, `assert_type` and typed `# type: ignore[code]` comments are the static tools the suites use, and [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}) teaches them.

## verify.sh and CI

`scripts/verify.sh` runs six steps in order and stops at the first failure.

| Step | Command |
| --- | --- |
| Sync | `uv sync --locked --all-packages` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format --check .` |
| Types per member | `cd <member> && uv run mypy --strict src tests`, for each member with a `pyproject.toml` |
| Types for scripts | `uv run mypy --strict scripts/validate.py scripts/render_diagrams.py` |
| Tests | `uv run pytest` |

The script's `set -e` stops at the first non-zero status, and the recorded runs show what each tool returns. `ruff check` and `ruff format --check` exit 1 on findings, `uv lock --check` exits 1 on a stale lockfile, mypy exits 1 on errors and 2 when it can't continue, and pytest exits 2 when collection fails.

CI's `python` job runs the script. Separate jobs run the book checks with `uv run --locked python scripts/validate.py` and its `--self-test`, and the free-threaded steps above. The `ci-ok` job passes only when every job it needs succeeded, so it is the one check a merge depends on.

## For deeper coverage

uv's documentation covers [projects and syncing](https://docs.astral.sh/uv/concepts/projects/sync/), [workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) and [project configuration](https://docs.astral.sh/uv/concepts/projects/config/). Ruff's covers [configuration](https://docs.astral.sh/ruff/configuration/), [settings](https://docs.astral.sh/ruff/settings/) and the [rules](https://docs.astral.sh/ruff/rules/). mypy's covers the [command line](https://mypy.readthedocs.io/en/stable/command_line.html) and the [configuration file](https://mypy.readthedocs.io/en/stable/config_file.html). [Prerequisites and the toolchain]({{ '/docs/00-prerequisites/' | relative_url }}) holds the install and the version table, and the books the book draws on are listed in the [bibliography]({{ '/bibliography/' | relative_url }}).
