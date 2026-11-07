---
title: "r20 toolchain runs (witness table A)"
output: false
render_with_liquid: false
---

# r20 evidence: toolchain runs for Appendix A

Recorded 2026-11-07 for step W1a of `_plans/r20-plan.md`, on branch `release/r20`. Every row of witness table A that names a "run" witness is below, with the exact command, the exit status and the quoted lines. Appendix A has no member; these runs and the fetched docs are its witnesses.

## Conditions

- Versions run: `uv 0.13.7 (x86_64-unknown-linux-gnu)`, `ruff 0.17.4`, `mypy 2.4.1 (compiled: yes)`, `pytest 9.2.0`, pytest-mock `3.17.0`, `Python 3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]` (default build) and `Python 3.15.2 free-threading build (main, Oct 26 2026, 14:06:54) [Clang 23.1.3 ]`. `.python-version` holds `3.15.2`.
- Counts (distributions, rules, files) are those of this repository at this commit. They are not claims about the tools in general.
- Two scratch copies, each built with `(git ls-files -z; git ls-files -z --others --exclude-standard) | xargs -0 cp --parents -t <dir>` and then `rm -rf .venv .venv-ft`. Neither has a `.git`. The first (`<copy>`, "copy 1") was synced and carries every row except the before-sync row. The second ("copy 2") was never synced before its before-sync row. Both were deleted afterwards.
- `UV_LINK_MODE=copy` was set for every run, only to silence uv's hardlink warning on the scratch filesystem. It changes no output quoted here.
- Output was passed through `python3 scripts/host_ids.py filter`, and scratch paths were replaced by `<copy>`. Commands are written relative to the repository root. Where a row changes directory it says so. The git identity that `uv init` writes was replaced by `<git user.name>` and `<git user.email>` by hand.
- Before the `.venv-ft` rows, copy 1's root `pyproject.toml` had no `.venv-ft` entry in `[tool.ruff] extend-exclude` (the copy was taken from the working tree before W0's edit landed). The "before" and "after" for that row are in one copy: the line was added with `sed` between them.
- No interpreter was downloaded: `uv python install` ran with `--offline` and reported both builds already installed.

## 1. `uv sync --locked --all-packages` (dev tools plus every member)

Copy 1, no `.venv`:

```
$ uv sync --locked --all-packages
Using CPython 3.15.2
Creating virtual environment at: .venv
Resolved 54 packages in 1ms
   Building adapter-facade-bridge @ file://<copy>/examples/19-adapter-facade-bridge
...
```

```
$ uv sync --locked --all-packages        (second run)
Resolved 54 packages in 1ms
Checked 52 packages in 0.73ms
```

Distributions in `.venv` afterwards (`importlib.metadata`, run with the venv's python): `52`. Exit 0.

## 2. `uv sync --locked` without `--all-packages` (exact sync removes the members)

Copy 1, after row 1:

```
$ uv sync --locked
Checked 13 packages in 0.07ms     (last line; exit 0)
```

Lines beginning ` - ` (packages removed): `39`, for example

```
 - adapter-facade-bridge==0.1.0 (from file://<copy>/examples/19-adapter-facade-bridge)
 - asyncio-patterns==0.1.0 (from file://<copy>/examples/38-asyncio-and-the-patterns)
 - builder-prototype==0.1.0 (from file://<copy>/examples/17-builder-dataclasses-and-prototype)
```

Distributions left: `13`:

```
['Pygments', 'ast_serialize', 'iniconfig', 'librt', 'mypy', 'mypy_extensions', 'packaging', 'pathspec', 'pluggy', 'pytest', 'pytest-mock', 'ruff', 'typing_extensions']
```

Then:

```
$ uv run --no-sync pytest -q examples/00-prerequisites
E   ModuleNotFoundError: No module named 'consignments'
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.07s
```

Exit status of pytest: 2. Restoring with `uv sync --locked --all-packages` printed 39 lines beginning ` + ` and the environment held `52` distributions again.

## 3. `uv run` from a member: before and after the root sync

Copy 2, no `.venv`, never synced:

```
$ cd examples/00-prerequisites && uv run pytest -q
Using CPython 3.15.2
Creating virtual environment at: <copy>/.venv
Installed 1 package in 1ms
error: Failed to spawn: pytest
  cause: No such file or directory (os error 2)
```

Exit 2. The environment it created held one distribution: `['consignments']`.

Then, still in copy 2, from the root, `uv sync --locked --all-packages` (environment now `52` distributions), and from the member directory:

```
$ cd examples/00-prerequisites && uv run pytest -q
..........................                                               [100%]
26 passed in 0.03s
```

Exit 0.

```
$ cd examples/00-prerequisites && uv run mypy --strict src tests
Success: no issues found in 3 source files
```

Exit 0.

```
$ cd examples/00-prerequisites && uv run python -c "import sys; print(sys.prefix)"
<copy>/.venv
```

The environment held `52` distributions after the member runs, the same as before them (inexact: nothing removed).

## 4. `--locked`, `--frozen`, `--all-packages`, `--python`, `uv lock --check`, `--upgrade-package`: help lines

`uv sync --help`:

```
      --locked
          Assert that the `uv.lock` will remain unchanged [env: UV_LOCKED=]
      --frozen
          Sync without updating the `uv.lock` file [env: UV_FROZEN=]
      --all-packages
          Sync all packages in the workspace
  -p, --python <PYTHON>      The Python interpreter to use for the project environment. [env:
                             UV_PYTHON=]
```

`uv lock --help`:

```
      --check            Check if the lockfile is up-to-date
      --check-exists     Assert that a `uv.lock` exists without checking if it is up-to-date [env:
                         UV_FROZEN=]
  -P, --upgrade-package <UPGRADE_PACKAGE>
          Allow upgrades for a specific package, ignoring pinned versions in any existing output
```

`uv run --help`:

```
      --locked
          Assert that the `uv.lock` will remain unchanged [env: UV_LOCKED=]
      --frozen
          Run without updating the `uv.lock` file [env: UV_FROZEN=]
```

`uv run --locked` is what CI's book checks use: `.github/workflows/ci.yml` lines 39 and 41 read `run: uv run --locked python scripts/validate.py` and `run: uv run --locked python scripts/validate.py --self-test`; line 28 is `run: bash scripts/verify.sh`.

## 5. `uv lock` and `uv lock --check`: current lockfile, then a stale pin

Copy 1, clean:

```
$ uv lock
Resolved 54 packages in 1ms
$ uv lock --check
Resolved 54 packages in 1ms
$ uv lock --check --offline
Resolved 54 packages in 1ms
```

All exit 0.

Root pin edited to `"ruff==0.17.3"` (`sed`, one line of `[dependency-groups] dev`):

```
$ uv lock --check
Resolved 54 packages in 117ms
error: The lockfile at `uv.lock` needs to be updated, but `--check` was provided.

hint: To update the lockfile, run `uv lock`.
```

Exit 1.

```
$ uv sync --locked --all-packages
Resolved 54 packages in 4ms
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.

hint: To update the lockfile, run `uv lock`.
```

Exit 1.

```
$ uv run --locked ruff --version
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.

hint: To update the lockfile, run `uv lock`.
```

Exit 1.

```
$ uv lock
Resolved 54 packages in 4ms
Updated ruff v0.17.4 -> v0.17.3
```

Exit 0; `uv.lock` changed by 20 insertions and 20 deletions. Pin and `uv.lock` were then restored byte for byte from the originals; `uv lock --check` printed `Resolved 54 packages in 1ms` (exit 0) and `uv run ruff --version` printed `ruff 0.17.4`.

## 6. `uv init --lib` in the workspace, both forms

Copy 1, no `.git`. Default flags apart from `--lib`:

```
$ uv init --lib examples/99-init-probe
Project `99-init-probe` is already a member of workspace `<copy>`
Initialized project `99-init-probe` at `<copy>/examples/99-init-probe`
```

Exit 0. Files created: `.git/`, `.gitignore`, `README.md`, `pyproject.toml`, `src/_99_init_probe/__init__.py`, `src/_99_init_probe/py.typed`. The root `pyproject.toml` was byte-identical afterwards. The generated `pyproject.toml`:

```
[project]
name = "99-init-probe"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
authors = [
    { name = "<git user.name>", email = "<git user.email>" }
]
requires-python = ">=3.15.2"
dependencies = []

[tool.uv.build-backend]
module-name = "_99_init_probe"

[build-system]
requires = ["uv_build>=0.13.7,<0.14.0"]
build-backend = "uv_build"
```

Directory removed. Second form:

```
$ uv init --lib --vcs none --no-readme --no-description --author-from none --name pytest-reference examples/99-init-probe
Project `pytest-reference` is already a member of workspace `<copy>`
Initialized project `pytest-reference` at `<copy>/examples/99-init-probe`
```

Exit 0. Files created (`find`):

```
99-init-probe
99-init-probe/pyproject.toml
99-init-probe/src
99-init-probe/src/pytest_reference
99-init-probe/src/pytest_reference/__init__.py
99-init-probe/src/pytest_reference/py.typed
```

No `.python-version` in the new directory. Root `pyproject.toml` byte-identical afterwards. The generated `pyproject.toml`:

```
[project]
name = "pytest-reference"
version = "0.1.0"
requires-python = ">=3.15.2"
dependencies = []

[build-system]
requires = ["uv_build>=0.13.7,<0.14.0"]
build-backend = "uv_build"
```

`__init__.py` holds `def hello() -> str:` returning `"Hello from pytest-reference!"`. For comparison, the repo's `examples/00-prerequisites/pyproject.toml` has `requires-python = ">=3.15"` and `requires = ["uv_build>=0.13.7,<0.14"]`: the two edits Appendix A names.

Help lines of `uv init --help` (the options the flag names rely on):

```
      --name <NAME>                    The name of the project
      --lib                            Create a project for a library
      --no-description                 Disable the description for the project
      --vcs <VCS>                      Initialize a version control system for the project [possible
                                       values: git, none]
      --no-readme                      Do not create a `README.md` file
      --author-from <AUTHOR_FROM>      Fill in the `authors` field in the `pyproject.toml` [possible
                                       values: auto, git, none]
      --no-pin-python                  Do not create a `.python-version` file for the project
```

## 7. `uv python install` and `uv python list --only-installed`

```
$ uv python install --offline 3.15.2
Python 3.15.2 is already installed
$ uv python install --offline 3.15.2t
Python 3.15.2+freethreaded is already installed
```

Exit 0 both. `uv python install --help` opens `Download and install Python versions` / `Usage: uv python install [OPTIONS] [TARGETS]...`.

```
$ uv python list --only-installed        (3.15 lines, paths removed)
cpython-3.15.2-linux-x86_64-gnu  <path>
cpython-3.15.2-linux-x86_64-gnu  <path>
cpython-3.15.2+freethreaded-linux-x86_64-gnu  <path>
cpython-3.15.2+freethreaded-linux-x86_64-gnu  <path>
```

Exit 0. `uv python list --help`: `--only-installed` / `Only show installed Python versions`.

## 8. Second environment: `UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15.2t --locked --all-packages`

Copy 1:

```
$ UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15.2t --locked --all-packages
Using CPython 3.15.2+freethreaded
Creating virtual environment at: .venv-ft
Resolved 54 packages in 1ms
Installed 52 packages in 42ms
```

Exit 0. A second run ended `Resolved 54 packages in 1ms` / `Checked 52 packages in 0.75ms`. `ls -d .venv .venv-ft` listed both. The GIL probe (`import sys, sysconfig; print(sys._is_gil_enabled(), sysconfig.get_config_var("Py_GIL_DISABLED"))`):

```
.venv-ft/bin/python   ->  False 1
.venv/bin/python      ->  True 0
```

`.venv-ft/bin/python -VV`: `Python 3.15.2 free-threading build (main, Oct 26 2026, 14:06:54) [Clang 23.1.3 ]`. `.venv/bin/python -VV`: `Python 3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`. Both environments held `52` distributions from the same `uv.lock` (unchanged: `Resolved 54 packages`). `ci.yml` lines 60 to 64 carry `uv python install 3.15.2t`, `UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15.2t --locked --all-packages` and `.venv-ft/bin/python -m pytest examples/37-the-gil-and-performance examples/38-asyncio-and-the-patterns`.

## 9. ruff and `.venv-ft`, in a copy without `.git`: before and after the `extend-exclude` line

Copy 1 has `.venv-ft` (row 8) and no `.git`. Before the line (`extend-exclude = ["_site", ".jekyll-cache", "vendor", ".bundle", "scripts/host_ids.py", "scripts/generate_diagram.py"]`):

```
$ uv run ruff check --output-format concise .
.venv-ft/bin/activate_this.py:29:6: RUF100 [*] Unused `noqa` directive (non-enabled: `D415`)
.venv-ft/bin/activate_this.py:44:101: E501 Line too long (103 > 100)
Found 2 errors.
[*] 1 fixable with `--fix`.
```

Exit 1.

```
$ uv run ruff format --check .
...
1 file would be reformatted, 610 files already formatted
```

Exit 1; the file is `.venv-ft/bin/activate_this.py` (the full-format block starts `unformatted: File would be reformatted` / ` --> .venv-ft/bin/activate_this.py:44:16`).

After `sed` made the line `extend-exclude = [".venv-ft", "_site", ".jekyll-cache", "vendor", ".bundle", "scripts/host_ids.py", "scripts/generate_diagram.py"]`:

```
$ uv run ruff check .
All checks passed!
$ uv run ruff format --check .
610 files already formatted
```

Exit 0 both.

Full gate with the line in place, in the same copy (`.venv-ft` present, no `.git`): `bash scripts/verify.sh` exit 0, `==> ruff check` `All checks passed!`, `==> ruff format --check` `610 files already formatted`, mypy per member and on scripts clean, `1312 passed in 155.98s (0:02:35)`, final line `verify: all steps passed`.

## 10. A member's tool table replaces the root's (mypy, ruff, pytest)

Copy 1. A probe module `examples/00-prerequisites/src/consignments/shadow_probe.py` held `def f(x):` / `    return x` and a 108-column line `LONG = "aaa...aaa"`; `examples/00-prerequisites/tests/test_shadow_probe.py` held a test that calls `warnings.warn("old", DeprecationWarning, stacklevel=1)`. Both were deleted afterwards and the member's `pyproject.toml` restored.

Root config only (member `pyproject.toml` has no tool table), from the member directory:

```
$ cd examples/00-prerequisites && uv run mypy src
src/consignments/shadow_probe.py:1: error: Function is missing a type annotation  [no-untyped-def]
Found 1 error in 1 file (checked 3 source files)
```

Exit 1.

```
$ cd examples/00-prerequisites && uv run ruff check --output-format concise src/consignments/shadow_probe.py
src/consignments/shadow_probe.py:5:101: E501 Line too long (108 > 100)
Found 1 error.
$ uv run ruff check --show-settings src/consignments/shadow_probe.py | grep -E 'Settings path|^linter.line_length'
Settings path: "<copy>/pyproject.toml"
linter.line_length = 100
```

```
$ cd examples/00-prerequisites && uv run pytest -q tests/test_shadow_probe.py
E       DeprecationWarning: old
FAILED tests/test_shadow_probe.py::test_warns - DeprecationWarning: old
1 failed in 0.02s
```

with `rootdir: <copy>` and `configfile: pyproject.toml` (the root file) in the header.

Member `pyproject.toml` with this appended:

```
[tool.mypy]
strict = false

[tool.ruff]
line-length = 120

[tool.pytest.ini_options]
addopts = ""
```

```
$ cd examples/00-prerequisites && uv run mypy src
Success: no issues found in 3 source files
$ uv run ruff check --output-format concise src/consignments/shadow_probe.py
All checks passed!
$ uv run ruff check --show-settings src/consignments/shadow_probe.py | grep -E 'Settings path|^linter.line_length'
Settings path: "<copy>/examples/00-prerequisites/pyproject.toml"
linter.line_length = 120
$ uv run pytest -q tests/test_shadow_probe.py
1 passed, 1 warning in 0.00s
```

with `rootdir: <copy>/examples/00-prerequisites` and `configfile: pyproject.toml` (the member's) in the pytest header. The pytest warning line read `...tests/test_shadow_probe.py:5: DeprecationWarning: old`. Exit 0 for each. The ruff witness uses `line-length`, not a rule family, because ruff's default set already includes `I` and `UP` (row 12).

## 11. ruff prefixes (`ruff linter`)

```
$ uv run ruff linter | grep -E "^ *(E|W|F|I|UP|B|SIM|RUF|PT|N)( |/)"
   B flake8-bugbear
  PT flake8-pytest-style
 SIM flake8-simplify
   I isort
   N pep8-naming
 E/W pycodestyle
   F Pyflakes
  UP pyupgrade
 RUF Ruff-specific rules
```

Exit 0. Ten prefixes (`E` and `W` share the pycodestyle line), matching the root `select = ["E", "F", "W", "I", "UP", "B", "SIM", "RUF", "PT", "N"]`.

## 12. Root `select` against ruff's default rule set

`uv run ruff check --show-settings examples/00-prerequisites/src/consignments/__init__.py` (root config) and the same with `--isolated`. Rules counted as lines between `linter.rules.enabled = [` and the closing `]`:

```
root config:  279 rules, settings path <copy>/pyproject.toml, linter.line_length = 100
--isolated:   407 rules, no "Settings path" line
```

Rules per leading letter group, root config (codes in the list, trailing digits removed): `B` 39, `E` 18, `F` 43, `I` 2, `N` 16, `PT` 28, `RUF` 52, `SIM` 30, `UP` 45, `W` 6; sum 279.

Rules per leading letter group with `--isolated`: `ASYNC` 10, `B` 29, `BLE` 1, `C` 17, `D` 1, `DTZ` 3, `E` 2, `EXE` 4, `F` 40, `FA` 2, `FLY` 1, `FURB` 17, `G` 4, `I` 1, `INT` 3, `ISC` 1, `LOG` 5, `N` 1, `PERF` 3, `PGH` 1, `PIE` 8, `PLC` 8, `PLE` 33, `PLR` 13, `PLW` 20, `PT` 6, `PTH` 2, `PYI` 47, `RET` 1, `RUF` 36, `S` 3, `SIM` 21, `T` 1, `TC` 4, `TRY` 5, `UP` 42, `W` 1, `YTT` 10; sum 407. That is 38 letter groups by this counting (the plan's "46 prefixes" counts finer prefixes such as `C4`, `C90`, `T10`, `T20`); `ASYNC`, `FURB`, `PLE`, `PYI` and `S` are among them.

`uv run ruff check --help` for the options: `--select <RULE_CODE>` "Comma-separated list of rule codes to enable (or ALL, to enable all rules)"; `--extend-select <RULE_CODE>` "Like --select, but adds additional rule codes on top of those already specified"; `--ignore <RULE_CODE>` "Comma-separated list of rule codes to disable"; `--isolated` "Ignore all configuration files".

## 13. `ruff check` and `ruff format` options (help lines)

`uv run ruff check --help`, option blocks verbatim:

```
      --fix
          Apply fixes to resolve lint violations. Use `--no-fix` to disable or `--unsafe-fixes` to
          include unsafe fixes
      --unsafe-fixes
          Include fixes that may not retain the original intent of the code. Use `--no-unsafe-fixes`
          to disable
      --show-fixes
          Show an enumeration of all fixed lint violations. Use `--no-show-fixes` to disable
      --diff
          Avoid writing any fixed files back; instead, output a diff for each changed file to
          stdout, and exit 0 if there are no diffs. Implies `--fix-only`
      --statistics
          Show counts for every rule with at least one violation
      --output-format <OUTPUT_FORMAT>
          Output serialization format for violations. The default serialization format is "full"

          [env: RUFF_OUTPUT_FORMAT=]
          [possible values: concise, full, json, json-lines, junit, grouped, github, gitlab, pylint,
          rdjson, azure, sarif]
      --show-settings
          See the settings Ruff will use to lint a given Python file
      --isolated
          Ignore all configuration files
      --target-version <TARGET_VERSION>
          The minimum Python version that should be supported

          [possible values: py37, py38, py39, py310, py311, py312, py313, py314, py315]
      --add-noqa[=<REASON>]
          Enable automatic additions of `noqa` directives to failing lines. Optionally provide a
          reason to append after the codes
      --ignore-noqa
          Ignore any `# noqa` comments
```

`uv run ruff format --help`:

```
      --check
          Avoid writing any formatted files back; instead, exit with a non-zero status code if any
          files would have been modified, and zero otherwise
      --diff
          Avoid writing any formatted files back; instead, exit with a non-zero status code and the
          difference between the current file and how the formatted file would look like
      --line-length <LINE_LENGTH>
          Set the line-length
      --target-version <TARGET_VERSION>
          The minimum Python version that should be supported

          [possible values: py37, py38, py39, py310, py311, py312, py313, py314, py315]
      --isolated
          Ignore all configuration files
```

`uv run ruff --help` command list: `check`, `rule`, `config`, `linter`, `clean`, `format`, `server`, `analyze`, `version`, `help`.

## 14. Behaviour of the `ruff check` options, `# noqa` and `RUF100`

Copy 1, scratch file `probe_dir/probe.py` (deleted afterwards), covered by the root config:

```
import sys
import os
from typing import Optional


def f(x: Optional[int]) -> int:
    return 0 if x is None else x


print(sys.argv)  # noqa: B018
```

```
$ uv run ruff check --output-format concise probe_dir/probe.py
probe_dir/probe.py:1:1: I001 [*] Import block is un-sorted or un-formatted
probe_dir/probe.py:2:8: F401 [*] `os` imported but unused
probe_dir/probe.py:6:10: UP045 [*] Use `X | None` for type annotations
probe_dir/probe.py:10:18: RUF100 [*] Unused `noqa` directive (unused: `B018`)
Found 4 errors.
[*] 4 fixable with `--fix`.
```

Exit 1. The same command with `--isolated` printed the same four lines (exit 1).

```
$ uv run ruff check --statistics probe_dir/probe.py
1	UP045 	[*] non-pep604-annotation-optional
1	I001  	[*] unsorted-imports
1	F401  	[*] unused-import
1	RUF100	[*] unused-noqa
Found 4 errors.
[*] 4 fixable with `--fix`.
```

Exit 1.

```
$ uv run ruff check --diff probe_dir/probe.py
--- probe_dir/probe.py
+++ probe_dir/probe.py
@@ -1,10 +1,8 @@
 import sys
-import os
-from typing import Optional
 
 
-def f(x: Optional[int]) -> int:
+def f(x: int | None) -> int:
     return 0 if x is None else x
 
 
-print(sys.argv)  # noqa: B018
+print(sys.argv)

Would fix 5 errors.
```

Exit 1 (not 0, although the file was left unchanged and the help line says "exit 0 if there are no diffs"; here there were diffs). The count says "5 errors" against the 4 reported by `check`.

The full-format `ruff check probe_dir/probe.py` block for the last finding:

```
RUF100 [*] Unused `noqa` directive (unused: `B018`)
  --> probe_dir/probe.py:10:18
   |
10 | print(sys.argv)  # noqa: B018
   |                  ^^^^^^^^^^^^
help: Remove unused `noqa` directive
```

## 15. `ruff format`, `ruff format --check`, `ruff format --diff`

`probe_dir/fmt.py` held `x = {'a':1}`:

```
$ uv run ruff format --check probe_dir/fmt.py
unformatted: File would be reformatted
 --> probe_dir/fmt.py:1:6
  |
  - x = {'a':1}
1 + x = {"a": 1}
  |

1 file would be reformatted
```

Exit 1; the file still held `x = {'a':1}` afterwards.

```
$ uv run ruff format --diff probe_dir/fmt.py
--- probe_dir/fmt.py
+++ probe_dir/fmt.py
@@ -1 +1 @@
-x = {'a':1}
+x = {"a": 1}

1 file would be reformatted
```

Exit 1.

```
$ uv run ruff format probe_dir/fmt.py
1 file reformatted
```

Exit 0; the file then held `x = {"a": 1}` and `ruff format --check` printed `1 file already formatted` (exit 0). `probe.py` above printed `1 file already formatted` under `ruff format --check` and `--diff` (exit 0). The repo's own `ruff format --check .` is row 9 and `verify.sh`'s second step.

## 16. `ruff rule <CODE>`

```
$ uv run ruff rule UP045 | head -5
# non-pep604-annotation-optional (UP045)

Derived from the **pyupgrade** linter.

Fix is sometimes available.
```

Exit 0. The page continues with "What it does", "Why is this bad?", "Example", "Fix safety" and "Options" sections.

## 17. mypy `--strict` flag list (verbatim, 2.4.1)

`uv run mypy --help`:

```
  --strict                  Strict mode; enables the following flags:
                            --disallow-any-generics, --disallow-subclassing-
                            any, --disallow-untyped-calls, --disallow-untyped-
                            defs, --disallow-incomplete-defs, --check-untyped-
                            defs, --disallow-untyped-decorators, --warn-
                            redundant-casts, --warn-unused-ignores, --warn-
                            return-any, --no-implicit-reexport, --strict-
                            equality, --extra-checks
```

Thirteen flags (hyphenation by the help wrapper): `--disallow-any-generics`, `--disallow-subclassing-any`, `--disallow-untyped-calls`, `--disallow-untyped-defs`, `--disallow-incomplete-defs`, `--check-untyped-defs`, `--disallow-untyped-decorators`, `--warn-redundant-casts`, `--warn-unused-ignores`, `--warn-return-any`, `--no-implicit-reexport`, `--strict-equality`, `--extra-checks`. `--warn-unreachable` is not in the list. Other help lines:

```
  --warn-unreachable        Warn about statements or expressions inferred to
                            be unreachable (inverse: --no-warn-unreachable)
  --config-file CONFIG_FILE
                            Configuration file, must have a [mypy] section
                            (defaults to mypy.ini, .mypy.ini, pyproject.toml,
                            setup.cfg)
  --python-version x.y      Type check code assuming it will be running on
                            Python x.y
  --enable-error-code NAME  Enable a specific error code
  --no-incremental          Disable module cache (inverse: --incremental)
  --cache-dir DIR           Store module cache info in the given folder in
                            incremental mode (defaults to '.mypy_cache')
```

Exit 0.

## 18. `--warn-redundant-casts` is in `--strict`; `--warn-unreachable` is not

`strict_probe.py` (deleted afterwards), run from `examples/00-prerequisites` with no root config (`--config-file /dev/null`):

```
from typing import cast

x: int = 1
y = cast(int, x)
if isinstance(x, str):
    z = 2
```

```
$ uv run mypy --strict --config-file /dev/null src/consignments/strict_probe.py
/dev/null: No [mypy] section in config file
src/consignments/strict_probe.py:4: error: Redundant cast to "int"  [redundant-cast]
Found 1 error in 1 file (checked 1 source file)
```

Exit 1.

```
$ uv run mypy --strict --config-file /dev/null --warn-unreachable src/consignments/strict_probe.py
/dev/null: No [mypy] section in config file
src/consignments/strict_probe.py:4: error: Redundant cast to "int"  [redundant-cast]
src/consignments/strict_probe.py:5: error: Subclass of "int" and "str" cannot exist: have distinct disjoint bases  [unreachable]
src/consignments/strict_probe.py:6: error: Statement is unreachable  [unreachable]
Found 3 errors in 1 file (checked 1 source file)
```

Exit 1. So the root's `warn_redundant_casts = true` repeats a flag `--strict` already sets; `warn_unreachable = true` adds the unreachable errors.

## 19. The root config applies from a member directory without flags

`unreach_probe.py` (deleted afterwards) held `x: int = 1` / `if isinstance(x, str):` / `    y = 2`. From `examples/00-prerequisites`:

```
$ uv run mypy src/consignments/unreach_probe.py
src/consignments/unreach_probe.py:2: error: Subclass of "int" and "str" cannot exist: have distinct disjoint bases  [unreachable]
src/consignments/unreach_probe.py:3: error: Statement is unreachable  [unreachable]
Found 2 errors in 1 file (checked 1 source file)
```

Exit 1 (the root `strict = true` and `warn_unreachable = true` applied; no flag given).

```
$ uv run mypy --config-file /dev/null src/consignments/unreach_probe.py
/dev/null: No [mypy] section in config file
Success: no issues found in 1 source file
```

Exit 0.

```
$ uv run mypy --no-strict src/consignments/unreach_probe.py
usage: mypy [-h] [-v] [-V] [more options; see below]
            [-m MODULE] [-p PACKAGE] [-c PROGRAM_TEXT] [files ...]
mypy: error: ambiguous option: --no-strict could match --no-strict-optional, --no-strict-equality, --no-strict-equality-for-none, --no-strict-bytes
```

Exit 2.

```
$ uv run mypy --strict --no-warn-unreachable src/consignments/unreach_probe.py
Success: no issues found in 1 source file
```

Exit 0. (The `Building consignments` / `Built consignments` / `Uninstalled 1 package` / `Installed 1 package` lines before the first output are uv rebuilding the editable member after the restored `pyproject.toml`.)

## 20. Duplicate module from the root; per-member runs pass

```
$ uv run mypy --strict examples/38-asyncio-and-the-patterns/tests examples/39-final-project/tests
examples/39-final-project/tests/conftest.py: error: Duplicate module named "conftest" (also at "examples/38-asyncio-and-the-patterns/tests/conftest.py")
examples/39-final-project/tests/conftest.py: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#mapping-file-paths-to-modules for more info
examples/39-final-project/tests/conftest.py: note: Common resolutions include:
examples/39-final-project/tests/conftest.py: note:     a) using `--exclude` to avoid checking one of them,
examples/39-final-project/tests/conftest.py: note:     b) adding `__init__.py` somewhere,
examples/39-final-project/tests/conftest.py: note:     c) using `--explicit-package-bases` or adjusting `MYPYPATH`
Found 1 error in 1 file (errors prevented further checking)
```

Exit 2.

```
$ for d in examples/38-asyncio-and-the-patterns examples/39-final-project; do (cd $d && uv run mypy --strict src tests); done
Success: no issues found in 15 source files
Success: no issues found in 17 source files
```

Exit 0 each. The per-member loop of `scripts/verify.sh` also passed for all members (row 9's full run).

## 21. `--enable-error-code deprecated`

Scratch directory `probe_dep` (deleted afterwards): `m.py` held `from warnings import deprecated` and a function `legacy_rate(w: Decimal) -> Decimal` decorated `@deprecated("use quote")`; `n.py` held `from decimal import Decimal` / blank / `from m import legacy_rate` / blank / `print(legacy_rate(Decimal(1)))`. Run from `probe_dep` with the root config found by walking up:

```
$ cd probe_dep && uv run mypy --strict n.py
Success: no issues found in 1 source file
```

Exit 0.

```
$ cd probe_dep && uv run mypy --strict --enable-error-code deprecated n.py
n.py:3: error: function m.legacy_rate is deprecated: use quote  [deprecated]
Found 1 error in 1 file (checked 1 source file)
```

Exit 1. The line is 3 here because of this file's layout; the plan's `n.py:1` was a different file.

## 22. Files the appendix cites (not runs)

- Root `pyproject.toml` (at the commit this run started from): `[tool.uv] package = false` and `default-groups = ["dev"]`; `[tool.uv.workspace] members = ["examples/*", "spikes/*"]`; `[[tool.mypy.overrides]] module = ["generate_diagram", "host_ids"]` with `ignore_errors = true`; `[tool.pytest.ini_options] addopts = "--import-mode=importlib --strict-markers --strict-config"`, `xfail_strict = true`, `filterwarnings = ["error"]`.
- `scripts/verify.sh` steps, in order: `uv sync --locked --all-packages`; `uv run ruff check .`; `uv run ruff format --check .`; per-member `cd "$d" && uv run mypy --strict src tests` over `examples/*/` and `spikes/*/` that hold a `pyproject.toml`; `uv run mypy --strict scripts/validate.py scripts/render_diagrams.py`; `uv run pytest`.

## Differences from the plan's evidence

- Row 12: the plan said the `--isolated` rules span 46 prefixes; counted by leading letters of the code the list holds 38 groups. The rule counts (279 and 407) match.
- Row 10: the long line is 108 columns, not 110.
- Row 8: the default build prints `True 0` (the plan recorded `True`); the free-threaded build prints `False 1` as planned.
- Row 9: `1 file would be reformatted, 610 files already formatted` where the plan recorded 609 (the copy holds one more tracked or untracked Python file than the planning copy; the counts are the copy's).
- Row 14: `ruff check --diff` exits 1 when it finds diffs and says `Would fix 5 errors` against 4 reported by `check`.
- Row 21: the deprecated call is reported at `n.py:3`, a layout difference only.

## Addendum 2026-11-07 (after W1b and W1c; W4)

Two updates, recorded on pytest 9.2.0, uv 0.13.7 and Python 3.15.2.

### Workspace counts after the new members

The workspace now has 41 members. Rows 1 to 3, 5 and 8 above were recorded before the 42 and 43 members existed. Their behaviour still holds, but their counts have changed:

- `uv sync --locked --all-packages` installs 54 distributions.
- A plain `uv sync --locked` removes all 41 members and leaves 13 distributions.
- `uv lock` reports `Resolved 56 packages`.

Appendix A uses these figures. They were reproduced in a fresh copy during W4a.

### pytest help lines (Appendix B options table)

`uv run pytest --help` prints these lines for the options the table names:

```text
  -p name               Early-load given plugin module name or entry point
  -q, --quiet           Decrease verbosity
  -s                    Shortcut for --capture=no
  --tb=style            Traceback print mode (auto/long/short/line/native/no)
  -v, --verbose         Increase verbosity
```
