# S4a: uv workspace, tool availability, and config discovery

Environment: uv 0.13.7, CPython 3.14.10, pytest 9.2.0, mypy 2.4.1, ruff 0.17.3.
Layout: virtual root (`package = false`, `[tool.uv.workspace] members = ["examples/*", "spikes/*"]`),
the single `dev` dependency group at the root, members built with `uv_build`.
Paths below are scrubbed to `<repo>`. Two throwaway members (`examples/zz-a`, `examples/zz-b`,
each with `tests/test_model.py` and `src/zz_*/model.py`, no `tests/__init__.py`) were created
for the experiment and deleted afterwards.

## a. Dev tools in a member directory

Root has `[tool.uv] default-groups = ["dev"]`. Fresh state (`rm -rf .venv`), then in a member:

| Command | Result |
|---|---|
| `uv run pytest` | `error: Failed to spawn: pytest` (only the member is synced; the root group is not) |
| `uv run --group dev pytest` | error: the member has no group `dev` |
| `uv run --all-groups pytest` | 1 passed |
| `uv run --all-packages pytest` | 1 passed |
| `uv sync --locked --all-packages` at root, then `uv run pytest` in member | 1 passed; `uv run mypy --strict src tests` succeeds |

Cause: inside a member, uv treats the member as the project, so the virtual root's
dependency group is not part of the resolve. Syncing with `--all-packages` includes the root.
The environment is the shared root `.venv`, and later plain `uv run` calls in any member reuse it.

Decision: keep one set of pins in the root `dev` group; document `uv sync --locked --all-packages`
as the one-time setup (it is also the CI step). `uv run --all-packages <cmd>` is the one-shot
alternative. Per-member dev groups were rejected because they duplicate the pins.

## b. Single root mypy run

```
$ uv run mypy --strict examples spikes
examples/zz-a/tests/test_model.py: error: Duplicate module named "test_model" (also at "examples/00-prerequisites/tests/test_model.py")
Found 1 error in 1 file (errors prevented further checking)

$ uv run mypy --strict --explicit-package-bases --namespace-packages examples spikes
(same Duplicate module error)
```

Without `tests/__init__.py`, same-basename test files collide, and `explicit_package_bases`
does not help because the module name is still `test_model` or `tests.test_model` in every member.
Checking only `examples/*/src spikes/*/src` from the root passes (8 files, distinct package
names), but leaves tests unchecked.

Decision: run mypy per member (`cd <member> && uv run mypy --strict src tests`), looped from the root with `for d in examples/*/ spikes/*/` (trailing slash, so files such as READMEs are skipped).
Adding `tests/__init__.py` was not chosen, to keep the layout minimal and avoid
import-mode interactions.

pytest from the root with the same-basename tests: `uv run pytest` collected and passed all
files (4 passed), because `--import-mode=importlib` does not need unique basenames.

## c. Which configuration applies from a member directory

All from `examples/zz-a` with config only in the root `pyproject.toml`:

- pytest: `rootdir: <repo>`, `configfile: pyproject.toml` (the root file; members have no
  `[tool.pytest.ini_options]`, so pytest walks up to the first file that has it).
- ruff: `Settings path: "<repo>/pyproject.toml"`, `line_width = 100`, `target_version = 3.14`;
  a file with lint and format errors produced `I001` and a format difference.
- mypy 2.4.1: `LOG: Config File: <repo>/pyproject.toml`; an untyped function yielded
  `[no-untyped-def]` with no `--strict` flag, so the root `[tool.mypy]` strict settings apply.

Caveat: a member `pyproject.toml` that later gains its own `[tool.ruff]`, `[tool.pytest.ini_options]`
or `[tool.mypy]` table would shadow the root's for that member, since discovery stops at the nearest file with the table.
Members therefore carry no tool tables.
