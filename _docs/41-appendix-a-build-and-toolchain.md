---
title: "Build and toolchain reference: uv, ruff, mypy"
order: 41
layout: tutorial
sectionid: docs
part: "appendices"
appendix: "A"
description: "Reference for the uv, ruff and mypy commands, the one root configuration each tool reads, and the traps between them."
---

## Learning objectives

By the end of this appendix you can:

- Find the uv, ruff or mypy command for a task and say what it does on the pinned versions.
- Say which file each tool reads, and why a member carries no tool table.
- Build and use the free-threaded environment from the same lockfile.
- Add a member and bump a pin without breaking `--locked`.

## Why this matters

The pinned toolchain is Python 3.15.2 (with the free-threaded 3.15.2t build), uv 0.13.7, ruff 0.17.4 and mypy 2.4.1. Install, sync and the full version table are in [Prerequisites and the toolchain]({{ '/docs/00-prerequisites/' | relative_url }}). The uv and ruff documentation carries no version, so flags and counts below come from recorded runs of the pinned binaries.

Each tool picks one configuration file and never merges:

| Tool | Rule | Source |
| --- | --- | --- |
| mypy | Walks up the file system; "there is no merging of configuration files" | [mypy configuration file](https://mypy.readthedocs.io/en/stable/config_file.html) |
| ruff | Closest file to each checked file; "Ruff does not merge settings across configuration files" | [ruff configuration](https://docs.astral.sh/ruff/configuration/) |
| pytest | First file found | [pytest reference]({{ '/docs/42-appendix-b-pytest/' | relative_url }}) |

So a `[tool.*]` table in a member's `pyproject.toml` replaces the root's for that member. In recorded runs, a member `strict = false` let an unannotated function through mypy, a member `line-length = 120` let a 108-column line through ruff, and a member `addopts = ""` let a `DeprecationWarning` through pytest. Members carry no tool table. Without one, all three tools find the root file from a member directory: ruff reports it as its settings path, pytest as its `configfile`, and mypy applies its strict settings with no flag.

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
| `uv run --locked <command>` | The same, and fails if `uv.lock` would change; the validate jobs in CI use it. |

"The workspace shares a single lockfile, ensuring that the workspace operates with a consistent set of dependencies" ([workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)). The root `pyproject.toml` is virtual: `package = false` forces "a project package not to be built and installed into the project environment" ([project configuration](https://docs.astral.sh/uv/concepts/projects/config/)). Its `members` globs cover every directory under `examples/` and one other top-level directory, and its default groups name the dev group of pytest, pytest-mock, ruff and mypy.

### Traps

- **A sync without `--all-packages` removes the members.** Exact syncing, the `uv sync` default, "means it will remove any packages that are not selected for installation", while `uv run` is inexact ([sync](https://docs.astral.sh/uv/concepts/projects/sync/)). `uv sync --locked` from the root took the environment from 55 distributions to 13, dropping all 42 members, and the next pytest run failed with `ModuleNotFoundError: No module named 'consignments'`.
- **Sync the root before `uv run` in a member.** Before the root sync, `uv run pytest -q` in a member built an environment holding that member alone and stopped with `error: Failed to spawn: pytest`. After it, the same command used the root `.venv`.
- **`--locked` refuses a stale lockfile.** With `ruff==0.17.4` edited to `ruff==0.17.3` and `uv.lock` untouched, `uv sync --locked --all-packages`, `uv run --locked` and `uv lock --check` all exited 1:

<!-- fmt:off -->
```text
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.

hint: To update the lockfile, run `uv lock`.
```
<!-- fmt:on -->

`--frozen` is looser: "Sync without updating the `uv.lock` file", where `--locked` is "Assert that the `uv.lock` will remain unchanged". Use `--locked`, so a stale lockfile stops the command. To bump a pin, change the `==` pin and run `uv lock`, which printed `Updated ruff v0.17.4 -> v0.17.3`.

## Adding a member

```bash
uv init --lib --vcs none --no-readme --no-description --author-from none --name <project> examples/<slug>
```

It creates `pyproject.toml`, `src/<package>/__init__.py` and `py.typed`, and leaves the root `pyproject.toml` unchanged, because the `examples/*` glob already covers the directory. Edit `requires-python` from `>=3.15.2` to `>=3.15` and the build requirement from `uv_build>=0.13.7,<0.14.0` to `<0.14`, then run `uv lock`:

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

Without the flags, `uv init` also writes a README, the placeholder description `Add your description here`, an `authors` entry with the git user's name and email and, outside a git checkout, a nested repository. Chapter directories start with a digit, so without `--name` a directory such as `99-init-probe` gets `module-name = "_99_init_probe"` in a `[tool.uv.build-backend]` table.

## The free-threaded environment

CI builds a second environment from the same lockfile and runs the two concurrency examples in it:

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

| Setting | Effect |
| --- | --- |
| `UV_PROJECT_ENVIRONMENT=.venv-ft` | Environment path; "If a relative path is provided, it will be resolved relative to the workspace root" |
| `--python 3.15.2t` | Selects the free-threaded interpreter from uv's store |
| `sys._is_gil_enabled()` | `False` in `.venv-ft/bin/python`, `True` in `.venv/bin/python` |

[The GIL and performance]({{ '/docs/37-the-gil-and-performance/' | relative_url }}) covers the two builds. Ruff's default exclude list names `.venv` and `venv` but not `.venv-ft`. In a git checkout, `.gitignore` and `respect_gitignore` skip it; outside one, `ruff check .` reported two findings in `.venv-ft/bin/activate_this.py`. The root `extend-exclude` names `".venv-ft"` for that reason.

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

The root configuration:

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

| Setting | Effect |
| --- | --- |
| `select` | Replaces the default rule set ("Unlike select, which replaces the default rule set when specified, extend-select adds to whatever rules are already active", [settings](https://docs.astral.sh/ruff/settings/)). `--show-settings` lists 279 enabled rules with the root file and 407 with `--isolated`, which adds linters such as `ASYNC`, `FURB`, `PLE`, `PYI` and `S`. |
| `line-length = 100` | A 108-column line fails with `E501 Line too long (108 > 100)`. |
| `quote-style = "double"` | `ruff format` rewrites `x = {'a':1}` to `x = {"a": 1}`. |
| `target-version = "py315"` | "Ruff will not propose changes using features that are not available in the given version." |

A `# noqa: CODE` comment suppresses one code on its line. One that suppresses nothing is itself a finding: `# noqa: B018` on `print(sys.argv)` is reported as `RUF100`. `--add-noqa` adds such comments to failing lines and `--ignore-noqa` ignores them; neither is used here.

## mypy: strict types

"The exact list of flags enabled by running --strict may change over time" ([command line](https://mypy.readthedocs.io/en/stable/command_line.html)). On 2.4.1, `mypy --help` lists thirteen.

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

"The --warn-unreachable flag is not automatically enabled by the strict flag", so the root turns it on. It also repeats `warn_redundant_casts`, which `--strict` already sets; the repeat is harmless.

<!-- fmt:off -->
```toml
[tool.mypy]
python_version = "3.15"
strict = true
warn_unreachable = true
warn_redundant_casts = true
```
<!-- fmt:on -->

"Most flags correspond closely to command-line flags": `strict = true` is `--strict`, `warn_unreachable` is `--warn-unreachable`, and `python_version` is `--python-version`. An `[[tool.mypy.overrides]]` table sets `ignore_errors = true` for two vendored script modules.

| Option | What it does here |
| --- | --- |
| `--strict` | The thirteen flags above; passed on the command line as well as set in the root file. |
| `--warn-unreachable` | Reports code that analysis finds unreachable or redundant. |
| `--config-file FILE` | Uses that file instead of discovery; `/dev/null` replaced the root file and printed `No [mypy] section in config file`. |
| `--enable-error-code NAME` | Turns on one error code. |

- **The root file applies from a member directory.** `if isinstance(x, str):` after `x: int = 1` gave two `[unreachable]` errors with no flags, and passed with `--config-file /dev/null`.
- **`--no-strict` isn't a flag.** mypy refuses it as ambiguous.
- **Some codes sit outside `--strict`.** A call to a `warnings.deprecated` function from another module passes `--strict` and fails with `--enable-error-code deprecated`: `function m.legacy_rate is deprecated: use quote  [deprecated]`.
- **Run mypy per member.** From the root, two members' tests collide on a shared module name and mypy exits 2:

<!-- fmt:off -->
```text
examples/39-final-project/tests/conftest.py: error: Duplicate module named "conftest" (also at "examples/38-asyncio-and-the-patterns/tests/conftest.py")
```
<!-- fmt:on -->

mypy suggests excluding a file, adding an `__init__.py`, or `--explicit-package-bases` or `MYPYPATH`. Looping over the members avoids all three. `mypy.api.run`, `assert_type` and typed `# type: ignore[code]` comments are covered in [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}).

## verify.sh and CI

`scripts/verify.sh` runs six steps under `set -e` and stops at the first failure.

| Step | Command |
| --- | --- |
| Sync | `uv sync --locked --all-packages` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format --check .` |
| Types per member | `cd <member> && uv run mypy --strict src tests`, for each member with a `pyproject.toml` |
| Types for scripts | `uv run mypy --strict scripts/validate.py scripts/render_diagrams.py` |
| Tests | `uv run pytest` |

| Tool | Non-zero exit |
| --- | --- |
| `ruff check`, `ruff format --check` | 1 on findings |
| `uv lock --check` | 1 on a stale lockfile |
| mypy | 1 on errors, 2 when it can't continue |
| pytest | 2 when collection fails |

CI's `python` job runs the script. Other jobs run `uv run --locked python scripts/validate.py`, its `--self-test` and the free-threaded steps. `ci-ok` passes only when every job it needs succeeded, so it's the one check a merge depends on.

## For deeper coverage

uv's documentation covers [projects and syncing](https://docs.astral.sh/uv/concepts/projects/sync/), [workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) and [project configuration](https://docs.astral.sh/uv/concepts/projects/config/). Ruff's covers [configuration](https://docs.astral.sh/ruff/configuration/), [settings](https://docs.astral.sh/ruff/settings/) and the [rules](https://docs.astral.sh/ruff/rules/). mypy's covers the [command line](https://mypy.readthedocs.io/en/stable/command_line.html) and the [configuration file](https://mypy.readthedocs.io/en/stable/config_file.html). [Prerequisites and the toolchain]({{ '/docs/00-prerequisites/' | relative_url }}) holds the install and the version table, and the [bibliography]({{ '/bibliography/' | relative_url }}) lists the books.
