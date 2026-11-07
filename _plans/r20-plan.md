---
title: "r20 plan: appendices A-C (toolchain, pytest, mocking references)"
order: 20
output: false
render_with_liquid: false
---

# r20: appendices A-C, the toolchain, pytest and mocking references

Opus-planned 2026-11-07. Branch `release/r20`, cut from main at 95f965d (the r19 merge, tagged `r19.x`). This file is the source of truth for r20 scope, criteria and status. Executors never edit it; the orchestrator updates the status board.

No pin changes this iteration. Python 3.15.2, uv 0.13.7, uv_build 0.13.7, pytest 9.2.0, pytest-mock 3.17.0, mypy 2.4.1 and ruff 0.17.4 are still the latest stable releases (checked 2026-11-07 from PyPI JSON `info.version` and upload dates: pytest 9.2.0 of 2026-10-27, pytest-mock 3.17.0 of 2026-10-17, ruff 0.17.4 of 2026-11-05, mypy 2.4.1 of 2026-10-28, uv and uv-build 0.13.7 of 2026-11-03; `python.org/ftp/python/` lists 3.15.0, 3.15.1, 3.15.2 and 3.16.0, `3.15.3/` is a 404 and `3.16.0/` holds only `Python-3.16.0a1.tgz`, a pre-release; local `uv --version` prints `uv 0.13.7`; in the scratch environment `pytest --version` prints `pytest 9.2.0`, `ruff --version` `ruff 0.17.4`, `mypy --version` `mypy 2.4.1 (compiled: yes)`, and `importlib.metadata.version("pytest-mock")` `3.17.0`). The docs that serve a version string agree: the mypy command-line page's title is "The mypy command line - mypy 2.4.1 documentation", pytest's `en/stable/changelog.html` opens with "pytest 9.2.0 (2026-10-27)", pytest-mock's `en/stable/` changelog opens with 3.17.0, and `docs.python.org/3/library/unittest.mock.html` carries "Python 3.15.2 documentation". uv's and ruff's docs carry no version string, so recorded runs of the pinned binaries are the witness for their flags (evidence A, W1a). W0 re-checks before any edit.

Exact identities, from `scripts/chapters.toml` and the `_docs` front matter (the front matter wins where the registry wording differs):
- Appendix A: slug `41-appendix-a-build-and-toolchain`, title "Build and toolchain reference: uv, ruff, mypy", part 14 (`appendices`), `appendix: "A"`, `kind = "appendix"`, `has_example = false`, `status = "stub"`. PDP-141.
- Appendix B: slug `42-appendix-b-pytest`, title "pytest reference", part 14, `appendix: "B"`, `kind = "appendix"`, `has_example = false` (W0 sets `true`, decision 1), `status = "stub"`. PDP-142.
- Appendix C: slug `43-appendix-c-mocking`, title "Mocking reference: unittest.mock and pytest-mock", part 14, `appendix: "C"`, `kind = "appendix"`, `has_example = false` (W0 sets `true`, decision 1), `status = "stub"`. PDP-143. The registry row says "pytest-mock and unittest.mock reference"; reader text uses the front-matter title.
- Each stub carries a `## Reference` heading that the draft replaces with the sections below.
- Part 14's blurb: "Reference material: build and toolchain, pytest, mocking, xUnit test patterns, a pattern-to-force quick reference, and programming principles reviewed in code."

`validate.py` for `kind = "appendix"`: SPINE is Learning objectives, Why this matters, For deeper coverage (`check_spine`). No figure is required (`kind != "appendix"` guards the one-figure rule), and none is planned. The word rules apply as for chapters: above 2,500 prose words is an error, below 1,900 a warning; `word_count` skips table rows, headings, fenced code, inline code and URLs, so reference tables don't count. The sidebar count runs only for `kind == "pattern"`. `has_example` is metadata only. Claims: a row's `source:` URL must appear in `_docs/<NN>-*.md` for the number in its Ch cell (41, 42 or 43), so every source row is closed by the appendix that links it. `check_stale_versions`, `check_banned`, `check_xrefs` and `check_templates` apply to the appendices and to the new READMEs and cards (risks).

Work items: PDP-141, PDP-142 and PDP-143, `todo` in `_plans/iteration-plan.md`. The iteration plan quotes no PRD intent for the appendices beyond the roadmap line ("r20 | Appendices A-C") and the part blurb. The binding intent is the domain-model rows A, B and C (evidence S) and the promises the chapters make (evidence S, "Promises").

## User decisions (owner to confirm)

0. **Step ids.** The steps are W0 to W6. The caller confirmed W is unused. Following r16 to r19, only suffixed ids are cited as `run:` tokens: `W1b`, `W1c`, `W4a`, `W4b` and `W4c`. Plain W0, W2, W3, W5 and W6 appear only in this plan's table. Two `run:` tokens cite recorded files: `run: _plans/evidence/r20-toolchain-runs.md` (written at W1a) and `run: _plans/evidence/r20-mock-census.md` (written at W2).

   **Recommend: yes.**

1. **Runnable members: A has none; B and C have one each.**
   - **A: no member.** Every statement in A is about a command, a flag or a configuration table, and its witness is a run of the pinned binary or the repo's own config. A test member would have to run uv inside pytest, which builds or rewrites a virtual environment, needs a workspace around it and, for `uv lock`, may reach the network: not hermetic and not deterministic. The witness is `_plans/evidence/r20-toolchain-runs.md`, recorded at W1a in a fresh scratch copy (each command, its exit status and the exact lines quoted, scrubbed), plus fetched docs and the gates that run the root config on every `verify.sh` (evidence C to J).
   - **B: `examples/42-appendix-b-pytest`** (project `pytest-reference`, package `pytest_reference`). ch11 promises that the pytest reference "lists the rest" of fixtures, parametrization and configuration, and most of the rest has no test in the book: scope order, duplicate ids, `RaisesGroup`, `check=`, `capsys`, `caplog`, import modes, the strictness options and the command-line options. pytest's own `pytester` fixture runs an inner pytest session in a temporary directory with its own configuration, which makes the configuration and command-line rows deterministic tests (evidence K to O). Rows that an existing test already witnesses cite that test instead of a new one.
   - **C: `examples/43-appendix-c-mocking`** (project `mocking-reference`, package `mocking_reference`). ch11 promises the rest of the mock API and ch33 says the API "is collected" in this appendix. The rest (`spec_set`, `seal`, `wraps`, iterable and callable `side_effect`, `mock_calls`, `call`, `ANY`, `assert_has_calls`, `reset_mock`, `patch.object`, `patch.dict`, `mocker.stop`, `spy`, `stub`, `resetall`, async doubles) is behaviour, so it needs tests; nine probe tests on pytest-mock 3.17.0 passed (evidence P). Mocks appear in the member's tests because the mock API is the subject, as in "Seams in Python"; `src` has none.

   **Recommend: yes.** Alternatives: (a) no members, every row a fetched doc page: this leaves behaviour claims (`resetall` scope, the context-manager warning failing under the root filter, the import-mode collision) unwitnessed on the pinned versions; (b) a member for A too: rejected above.

2. **Depth and length.** Each appendix is a reference, not a lesson: tables carry the items, prose carries what a table can't (the rule, the trap, the pointer). Target about 1,600 to 2,200 prose words each by `validate.py`; the 2,500 ceiling is an error; a warning below 1,900 is reported and never padded (owner decision 2026-11-05). Each table row names its witness in the per-row witness tables below, so depth is bounded by what can be witnessed: an item with no witness is cut, not written. At most six excerpts per appendix, no figure, no experiments (decision 9). Every appendix opens with what it isn't: A doesn't repeat the install, sync and gate walkthrough of "Prerequisites and the toolchain"; B and C don't repeat the method and the doubles table of "Proving it works: pytest, pytest-mock, and mypy".

   **Recommend: yes.** Alternative: a shorter appendix (about 900 to 1,200 words) of tables only. The traps (exact sync, first config wins, `.venv-ft` outside git, the context-manager warning) need a sentence each to be usable.

3. **Appendix C shows `mocker`, after the book's rule.** `mocker` is how the book reaches the mock API in all three chapters that use mocks (`mocker.create_autospec` in "ISP, DIP, and dependency injection without a framework" and "Proving it works: pytest, pytest-mock, and mypy"; `mocker.Mock`, `mocker.patch` in "Seams in Python: monkeypatch, injection, and duck typing"), and the appendix's title names pytest-mock. C opens with the book's order of preference, stated once and witnessed by the census (evidence Q): a fake passed through a parameter first, because mypy checks it; `create_autospec` where the calls themselves are the claim, because it checks names and signatures at run time while mypy accepts any mock; a patch only where the code takes no parameter ("Seams in Python" and "Dependency-breaking techniques for modern Python"). The reference rows then list `unittest.mock` names, reached through `mocker` where pytest-mock offers them. C says once that a mock bypasses the static check (CLAUDE.md, "Example code").

   Correction to the brief: mocks aren't confined to the seams chapter and one dependency-breaking fixture. The census (evidence Q) finds `mocker`/`unittest.mock` in the tests of ch06, ch11 and ch33, and `monkeypatch` alone in ch03, ch11, ch33 and ch34 (ch34's one fixture uses `monkeypatch`, not a mock). No `src` in the repo imports a mock or `monkeypatch`. C's census table uses these facts.

   **Recommend: yes.** Alternative: `unittest.mock` only, with `mocker` in one row. That contradicts how the book's tests are written.

4. **No AI sidebar in any appendix.** The r19 census (`_plans/evidence/r19-sidebar-census.md`) records that appendices 41 to 46 have none, the validator requires one only for pattern chapters, and the testing sidebar already lives in "Proving it works: pytest, pytest-mock, and mypy" (a prompt for `create_autospec` doubles and the strict configuration). A reference appendix has no decision rule of its own for a prompt to bake in.

   **Recommend: yes.** Alternative: one sidebar in C (a prompt that asks for a fake through a parameter before a mock). It would restate ch11's sidebar.

5. **Citation set** (evidence R). Primary sources for the pinned versions, quoted exactly and only where fetched:
   - A: uv's projects/sync, workspaces, projects/config and CLI reference pages; ruff's configuration, settings and rules pages; mypy's command-line and configuration-file pages (2.4.1).
   - B: pytest's API reference, configuration ("customize"), "pytest import mechanisms and sys.path/PYTHONPATH" and plugins pages (stable is 9.2.0).
   - C: the Python 3.15.2 `unittest.mock` page, pytest-mock's usage page (3.17.0), typeshed's `stdlib/unittest/mock.pyi` (already cited by ch11), and Martin Fowler's "Mocks Aren't Stubs" (already cited by ch11) by title and topic.
   - Books already in `bibliography.html`: Brian Okken's *Python Testing with pytest*, second edition (B), and Gerard Meszaros's *xUnit Test Patterns* (C, for the double names only). No new book; nothing copied beyond quoted sentences; every quote stops where the page's sentence stops.

   **Recommend: yes.** Alternative: add Claudio Jolowicz's *Hypermodern Python Tooling* (O'Reilly) to the bibliography and hub for A. Its edition, date and coverage of uv weren't verified at planning; W4a would have to verify them, and the hub entry needs its own PR.

6. **Fix a wrong sentence in "Prerequisites and the toolchain" now (fix-now rule).** ch00 says: "`--all-packages` matters because the dev tools belong to the root, not to a member: inside a member directory uv treats the member as the project and wouldn't install pytest or mypy." From the root, a plain `uv sync --locked` installs the dev tools (13 distributions, `pytest`, `pytest-mock`, `mypy` and `ruff` among them) and removes all 39 members, after which pytest fails to import `consignments` (evidence C). `--all-packages` matters because of the members. The second half of the sentence (a member directory before the root sync) holds (evidence D). W4a rewrites that one sentence in ch00 with row 278 as its witness; nothing else in ch00 changes.

   **Recommend: yes.** Alternative: leave ch00 and state the correct reason only in A. The two pages would then disagree.

7. **Exclude `.venv-ft` in the root ruff config.** ruff skips `.venv` by default but not `.venv-ft`. In a git checkout `.gitignore` hides it (`respect_gitignore = true`); in a copy without `.git` (every scratch copy the iterations build, or a downloaded archive) with the free-threaded environment present, `ruff check .` reports `RUF100` and `E501` in `.venv-ft/bin/activate_this.py` and `ruff format --check .` reports one file to reformat, so `verify.sh` fails at its second step (evidence I). W0 adds `".venv-ft"` to `[tool.ruff] extend-exclude`; A describes the line.

   **Recommend: yes.** Alternative: document it as a trap and change nothing. The next scratch-copy run with `.venv-ft` would trip it.

8. **Keep the pytest configuration as it is; A and B document the pytest 9 forms.** pytest 9 adds a `[tool.pytest]` table with native TOML types and a `strict = true` option that enables `strict_config`, `strict_markers`, `strict_parametrization_ids` and `strict_xfail`, and renames `xfail_strict` to `strict_xfail` with the old name kept as an alias (evidence K). The root suite collects with no error under `-o strict=true` (evidence K), so a switch is possible, but it would change the three lines "Proving it works: pytest, pytest-mock, and mypy" describes and quotes in its experiments. B documents both forms with sources; the repo keeps `[tool.pytest.ini_options]`, `--strict-markers --strict-config` and `xfail_strict = true`.

   **Recommend: yes (no change in r20).** Alternative: switch to `[tool.pytest]` with `strict = true` and update ch11's configuration section and experiments four and five in the same iteration.

9. **Keep ruff's `select`; A states what it replaces.** ruff 0.17.4 has a default rule set (407 rules enabled with `--isolated`); the root `select` of ten linters replaces it with 279 rules (evidence I). Moving to `extend-select` on top of the defaults raises 80 findings across the repo (47 `FURB157`, 19 `S102`, 4 `BLE001`, 3 `PLR0124`, 2 `ISC004`, 2 `EXE001`, 2 `PYI055`, 1 `FLY002`). A reference iteration isn't the place for that churn.

   **Recommend: yes (no change in r20).** Alternative: adopt the defaults plus the current selection and fix or justify the 80 findings, as a separate iteration (r25 QA sweep).

10. **Keep `warn_redundant_casts = true` in `[tool.mypy]`.** mypy 2.4.1's `--strict` already enables `--warn-redundant-casts` (evidence H), so the line is redundant but harmless and explicit. `warn_unreachable = true` is the line that adds something: the docs say "the --warn-unreachable flag is not automatically enabled by the strict flag." A states both facts.

    **Recommend: yes.** Alternative: delete the redundant line (one-line config change, no test impact expected; W0 would re-run `verify.sh`).

11. **Enable `pytester` in B's test modules, not in a conftest or the root config.** `pytest_plugins = ["pytester"]` in the member's `tests/conftest.py` passes when pytest runs from the member directory and breaks the root collection with "Defining 'pytest_plugins' in a non-top-level conftest is no longer supported" (evidence M). The same line in a test module (after its imports, for ruff `E402`) loads the plugin from either directory with no warning, which pytest's plugins page documents ("You can require plugins in a test module or a conftest file using pytest_plugins"). `-p pytester` in the root `addopts` would also work but changes every member's configuration. The trap itself becomes a B row (test 30).

    **Recommend: yes.**

12. **Free-threaded CI job: neither member joins.** The r18 job is scoped to the chapters whose subject is the build. Both probe members gave the same results on `3.15.2t` (`sys._is_gil_enabled()` `False`) as on the default build (evidence J). `ci.yml` is unchanged.

    **Recommend: yes.**

13. **Domain names** come from `_plans/shipping-domain-model.md` only. B's `src` is in the Rating area: `ConsignmentId`, `Weight`, `Consignment(id, zone, weight)`, `RATES` (read-only `frozendict`, `EU` 0.45 and `ASIA` 1.20, illustrative), `RatingError`, `OverweightError`, `quote`, `rate_batch`, `legacy_quote` (deprecated), `write_quotes`. C's `src` is in the Carrier area: `ConsignmentId`, `CarrierQuote`, `CarrierTimeoutError`, `CarrierGateway` (Protocol), `FastlineGateway` (deterministic stand-in), `book_cheapest`, `Notify`, `confirm` (async). Carrier codes `FASTLINE` and `AIRCO` only. No new domain area. Domain rows A to C are updated at W0 to name the members.

    **Recommend: yes.**

14. **No cross-language wording, no project-outcome statistics, no chapter numbers** in reader text; pointers by exact front-matter title (evidence S). Counts in reader text are counts of the repo's own config or runs (rules enabled, distributions installed), each with its witness, never claims about other projects.

    **Recommend: yes.**

Also proposed for the owner (no decision needed unless declined):
- **Status hygiene at W0**: r19 is merged (95f965d) and tagged `r19.x`, but `iteration-plan.md` marks r19 "(active)" and PDP-139a to 140c `active`, and r19's V6 and V7 read `todo`. The orchestrator closes them.
- **A dated r20 note** in `_plans/spikes.md` at W2: evidence C to P.
- **`uv init` identity hazard.** Without `--author-from none`, `uv init` writes the git user's name and email into the new `pyproject.toml` (evidence F). The member steps use the flag, and A recommends it.

## Planning evidence

Probes ran in a scratch copy at `<scratchpad>/plan20`, built with `(git ls-files -z; git ls-files -z --others --exclude-standard) | xargs -0 cp --parents -t <dir>`, then `rm -rf .venv .venv-ft` and `uv sync --locked --all-packages`; one second copy (`plan20b`) tested a member run before the root sync. Two probe members were added there (`examples/42-probe`, package `pytest_probe`; `examples/43-probe`, package `mock_probe`) with `uv lock`. Sources were fetched into `<scratchpad>/fetch20`. All three directories were deleted afterwards; the repo was unchanged (`git status` clean). No host change was made: the free-threaded interpreter was already in uv's store from r18.
- Runtime: `Python 3.15.2 (main, Oct 26 2026, 14:06:56) [Clang 23.1.3 ]`.
- Baseline: `1312 passed in 149.57s (0:02:29)` from the root; 915 `def test_` lines across `examples` and `spikes`; 33 `test_static.py` files; 37 member conftests; `_data/diagrams.yml` has 41 entries.

The probes are reduced models: names follow the domain model, but messages, counts and line numbers are predictions until the build quotes them as observed.

**A. Pins and version witnesses.** See the header. For each command and flag A states, W1a records the pinned binary's `--help` line (uv 0.13.7, ruff 0.17.4, mypy 2.4.1, pytest 9.2.0) in the run file, because uv's and ruff's docs aren't versioned. Help lines observed at planning (exact): `uv sync --help`: `--locked` "Assert that the `uv.lock` will remain unchanged [env: UV_LOCKED=]", `--frozen` "Sync without updating the `uv.lock` file [env: UV_FROZEN=]", `--all-packages` "Sync all packages in the workspace", `-p, --python <PYTHON>` "The Python interpreter to use for the project environment."; `uv lock --help`: `--check` "Check if the lockfile is up-to-date", `-P, --upgrade-package <UPGRADE_PACKAGE>` "Allow upgrades for a specific package, ignoring pinned versions in any existing output"; `uv init --help`: `--lib`, `--vcs <VCS>` (git, none), `--no-readme`, `--no-description`, `--author-from <AUTHOR_FROM>` (auto, git, none), `--name`, `--no-pin-python`; `uv python list --help`: `--only-installed`. `UV_PROJECT_ENVIRONMENT` is not in `uv sync --help`; the projects/config page documents it (evidence R).

**B. Baseline.** As above.

**C. Exact sync and `--all-packages`.** In the scratch copy, `uv sync --locked` from the root (no `--all-packages`) removed every member (`- value-semantics==0.1.0 ...` and so on) and left 13 distributions: `['Pygments', 'ast_serialize', 'iniconfig', 'librt', 'mypy', 'mypy_extensions', 'packaging', 'pathspec', 'pluggy', 'pytest', 'pytest-mock', 'ruff', 'typing_extensions']`. `uv run --no-sync pytest -q examples/00-prerequisites` then failed collection with `E   ModuleNotFoundError: No module named 'consignments'`. `uv sync --locked --all-packages` restored 52 distributions. The sync page says: "uv sync performs "exact" syncing by default, which means it will remove any packages that are not selected for installation." This contradicts ch00's stated reason for `--all-packages` (decision 6).

**D. `uv run` in a member.** In a fresh copy with no `.venv`, `cd examples/00-prerequisites && uv run pytest -q` printed `Installed 1 package` then `error: Failed to spawn: pytest` / `cause: No such file or directory (os error 2)`; the environment held `['consignments']` only. After the root sync, `uv run pytest -q` from the same directory gave `26 passed`, `uv run mypy --strict src tests` gave `Success: no issues found in 3 source files`, `sys.prefix` was the root `.venv`, and the distribution count stayed 52 before and after (inexact). The sync page: "In contrast, uv run uses "inexact" syncing by default, ensuring that all required packages are installed but not removing extraneous packages." `examples/README.md` already says the same ("Without it, `uv run` inside an example installs only that example and the shared tools are missing").

**E. Stale lockfile.** `uv lock --check` on the clean copy: `Resolved 54 packages in 1ms`, exit 0. With `ruff==0.17.3` written into the root pin: `uv lock --check` printed `error: The lockfile at `uv.lock` needs to be updated, but `--check` was provided.` and `hint: To update the lockfile, run `uv lock`.`; `uv sync --locked --all-packages` printed the same with `--locked` in place of `--check` and exited 1. Pin restored, `--check` clean again.

**F. `uv init --lib` in the workspace.** `uv init --lib examples/99-init-probe` (no other flags) in the scratch copy, which has no `.git`, created a nested `.git/` with hooks, a `.gitignore`, a `README.md`, `src/_99_init_probe/__init__.py` and `py.typed`, a `pyproject.toml` with `description = "Add your description here"`, an `authors` entry taken from the git identity (name and email), `requires-python = ">=3.15.2"`, `[tool.uv.build-backend] module-name = "_99_init_probe"` (the directory name starts with a digit) and `requires = ["uv_build>=0.13.7,<0.14.0"]`. It printed "Project `99-init-probe` is already a member of workspace ..." and left the root `pyproject.toml` unchanged (the `examples/*` glob already covers it). With `--lib --vcs none --no-readme --no-description --author-from none --name pytest-reference`, it created only `pyproject.toml`, `src/pytest_reference/__init__.py` and `src/pytest_reference/py.typed`; no `[tool.uv.build-backend]` table, no authors. The repo's members write `requires-python = ">=3.15"` and `<0.14`; A says the member steps edit both to match (W1b, W1c). Inside the real repo `uv init` wouldn't create a nested `.git` (W1a confirms with `--vcs none` regardless).

**G. A member table shadows the root.** With `[tool.mypy] strict = false` appended to a probe member's `pyproject.toml`, `uv run mypy src` from that member passed a function with no annotations (`Success: no issues found in 3 source files`); with the table removed it reported `Function is missing a type annotation  [no-untyped-def]`. With `[tool.pytest.ini_options] addopts = ""` in the member, running pytest from the member used the member file: the mocker context-manager test that fails under the root filter passed with `11 passed, 1 warning`. With `[tool.ruff] line-length = 120` in the member, `ruff check --show-settings` named the member's `pyproject.toml` as "Settings path" and showed `linter.line_length = 120`. Each tool's docs say there is no merging (evidence R). Because ruff 0.17.4's default set includes `I` and `UP` rules (evidence I), the ruff witness must use `line-length` (a 110-column line flagged by the root, not by the member), not a rule family (W1a).

**H. mypy 2.4.1.**
- `mypy --help`: "--strict  Strict mode; enables the following flags: --disallow-any-generics, --disallow-subclassing-any, --disallow-untyped-calls, --disallow-untyped-defs, --disallow-incomplete-defs, --check-untyped-defs, --disallow-untyped-decorators, --warn-redundant-casts, --warn-unused-ignores, --warn-return-any, --no-implicit-reexport, --strict-equality, --extra-checks" (help wraps the lines; W1a records them verbatim). `--warn-unreachable` is a separate flag.
- From a member directory with no `--strict`, the root config applies: a scratch module `x: int = 1` / `if isinstance(x, str):` / `y = 2` gave `Subclass of "int" and "str" cannot exist: have distinct disjoint bases  [unreachable]` and `Statement is unreachable  [unreachable]`. `--config-file /dev/null` gave `/dev/null: No [mypy] section in config file` and then `Success`.
- `mypy --strict examples/38-asyncio-and-the-patterns/tests examples/39-final-project/tests` from the root: `examples/39-final-project/tests/conftest.py: error: Duplicate module named "conftest" (also at "examples/38-asyncio-and-the-patterns/tests/conftest.py")`, three resolution notes, `Found 1 error in 1 file (errors prevented further checking)`, exit 2.
- `--no-strict` is refused: `mypy: error: ambiguous option: --no-strict could match --no-strict-optional, --no-strict-equality, --no-strict-equality-for-none, --no-strict-bytes`.
- The `deprecated` code is not on under `--strict`: a call to a `@warnings.deprecated` function imported from another module passed `--strict`; with `--enable-error-code deprecated` it gave `n.py:1: error: function m.legacy_rate is deprecated: use quote  [deprecated]`.
- Help lines for `--python-version x.y`, `--config-file`, `--cache-dir DIR`, `--no-incremental`, `--enable-error-code NAME` exist as quoted in the run file.

**I. ruff 0.17.4.**
- `ruff linter` maps the root's prefixes: `B` flake8-bugbear, `PT` flake8-pytest-style, `SIM` flake8-simplify, `I` isort, `N` pep8-naming, `E/W` pycodestyle, `F` Pyflakes, `UP` pyupgrade, `RUF` Ruff-specific rules.
- `ruff check --show-settings` on a file: the enabled-rules list has 281 lines with the root config and 409 with `--isolated` (the list's two bracket lines included), so 279 against 407 rules; W1a re-derives the exact counts. With `--isolated` the enabled rules span 46 prefixes, including `ASYNC`, `FURB`, `PLE`, `PYI` and `S`. The rules page says "By default, Ruff enables rules from the F, E, B, UP, and RUF categories, as well as many more, omitting any stylistic rules that overlap with the use of a formatter".
- A scratch file with an unused `os`, `Optional[int]` and unsorted imports gave `I001`, `F401` and `UP045` both under the root config and under `--isolated`.
- Defaults plus the root's ten prefixes through `extend-select` over the repo: `Found 80 errors.` (decision 9).
- `.venv-ft` in a copy without `.git`: `ruff check .` gave `.venv-ft/bin/activate_this.py:29:6: RUF100 [*] Unused `noqa` directive (non-enabled: `D415`)` and `.venv-ft/bin/activate_this.py:44:101: E501 Line too long (103 > 100)`; `ruff format --check .` gave `1 file would be reformatted, 609 files already formatted`. In the git checkout both pass (`file_resolver.respect_gitignore = true`). With `.venv-ft` added to `extend-exclude`: `All checks passed!` (decision 7). The default `file_resolver.exclude` lists `.venv` and `venv`, not `.venv-ft`.
- `ruff check --help` lists `--fix`, `--unsafe-fixes`, `--show-fixes`, `--diff`, `--statistics`, `--output-format`, `--show-settings`, `--select`, `--extend-select`, `--ignore`, `--isolated`, `--target-version`, `--add-noqa`; `ruff format --help` lists `--check`, `--diff`, `--line-length`, `--target-version`, `--isolated`. An unused `# noqa: B018` gave `RUF100 [*] Unused `noqa` directive (unused: `B018`)`.

**J. Free-threaded environment.** `UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15.2t --locked --all-packages` built the second environment; `.venv-ft/bin/python -c "import sys,sysconfig; ..."` printed `False 1` (`sys._is_gil_enabled()`, `Py_GIL_DISABLED`); the default `.venv` printed `True`. Both probe members gave the same outcome on both builds (14 passed, 2 failed: the two probes written to fail). `uv python list --only-installed` lists `cpython-3.15.2+freethreaded-linux-x86_64-gnu` beside `cpython-3.15.2-linux-x86_64-gnu` (paths scrubbed). The python-versions page says that from 3.14 a free-threaded interpreter may be used without explicit selection while the GIL build is preferred; A doesn't quote that sentence (it names an older minor, risk "stale versions") and says only what the commands do.

**K. pytest configuration (9.2.0).**
- An inner `pytester` session has its own configuration: a test that warns `DeprecationWarning` gave `assert_outcomes(passed=1, warnings=1)` inside an outer session running under `filterwarnings = ["error"]`.
- The reference page: `strict` "If set to true, enable “strict mode”, which enables the following options: strict_config strict_markers strict_parametrization_ids strict_xfail", "Added in version 9.0."; `strict_xfail` "Changed in version 9.0: Renamed from xfail_strict to strict_xfail. xfail_strict is accepted as an alias for strict_xfail."; `strict_parametrization_ids` "If set to true, pytest emits an error if it detects non-unique parameter set IDs."; `strict_config` "If set to true, any warnings encountered while parsing the pytest section of the configuration file will raise errors."; `strict_markers` "If set to true, markers not registered in the markers section of the configuration file will raise errors."
- `uv run pytest --co -q -o strict=true` over the whole repo (with the two probe members) collected 1317 tests with no error (1312 plus 5 probes).
- `pytest --help` lists `--strict-config` "Enables the strict_config option", `--strict-markers` "Enables the strict_markers option" and `--strict` "Enables the strict option".
- The configuration page: "Use [tool.pytest] to leverage native TOML types (supported since pytest 9.0)" and "Use [tool.pytest.ini_options] for INI-style configuration (supported since pytest 6.0)"; "Options from multiple configfiles candidates are never merged - the first match wins."

**L. Import modes.** In `pytester` projects:
- two directories each holding `tests/test_model.py` and no `__init__.py`: `--import-mode=prepend` stopped at collection (`collected 1 item / 1 error`, `import file mismatch:`, `Interrupted: 1 error during collection`, `1 error`); `--import-mode=importlib` ran both (`2 passed`).
- a `tests/conftest.py` holding `LIMIT = 3` and a test module that does `from conftest import LIMIT`: passes under prepend; under importlib the module fails to import with `ModuleNotFoundError: No module named 'conftest'` (`errors=1`).
- The pythonpath page: "importlib: this mode uses more fine control mechanisms provided by importlib to import test modules, without changing sys.path."; "Test module names do not need to be unique" (the page continues after a dash with the rule that pytest generates a unique name from the rootdir; quote up to "unique" or paraphrase, criterion 13); "Test modules can’t import each other."
- `pytester`'s base temporary directory sits in a folder named after the account under the system temporary directory, so any quoted inner output names the account and must pass `host_ids.py filter` before quoting; no test asserts a path.

**M. Enabling `pytester`.** `pytest_plugins = ["pytester"]` in `examples/42-probe/tests/conftest.py`: `1 passed` from the member directory and from `uv run pytest -q examples/42-probe`; a whole-repo `uv run pytest --co -q` gave `ERROR examples/42-probe/tests - Failed: Defining 'pytest_plugins' in a non-to...` and `1312 tests collected, 1 error`, with the link `https://docs.pytest.org/en/stable/deprecations.html#pytest-plugins-in-non-top-level-conftest-files`. The same line in the test module: `1 passed` from the member and `1313 tests collected` from the root, no warning. The plugins page: "You can require plugins in a test module or a conftest file using pytest_plugins" and "Requiring plugins using a pytest_plugins variable in non-root conftest.py files is deprecated." (decision 11).

**N. Command-line options through `pytester`.** In a file with `test_ok` then a failing `test_bad`: a plain run gave `1 failed, 1 passed`; `--lf` printed `run-last-failure: rerun previous 1 failure` and `1 failed` (no deselected count in the summary); `-k ok` gave `1 passed, 1 deselected`; `-x` gave `1 failed, 1 passed`, which can't witness `-x` because the failure was last (W1b puts the failure first and asserts the later test didn't run). `pytest --help` lines recorded at planning: `-k EXPRESSION`, `-m MARKEXPR`, `-x, --exitfirst` "Exit instantly on first error or failed test", `--lf, --last-failed` "Rerun only the tests that failed at the last run (or all if none failed)", `--ff, --failed-first`, `--sw, --stepwise`, `--collect-only, --co`, `--import-mode={prepend,append,importlib}`, `-s` "Shortcut for --capture=no", `--tb=style`, `--durations=N`, `-q, --quiet`, `-v, --verbose`.

**O. Other pytest features.** One scratch test file, `9 passed`, mypy `--strict` and ruff clean:
- a module-scoped yield fixture under a function-scoped one: `ORDER` read in the second test was `["outer-setup", "inner-setup", "inner-teardown", "inner-setup"]`;
- `capsys.readouterr().out == "booked CN-1\n"` (typed `pytest.CaptureFixture[str]`);
- `caplog.at_level(logging.INFO)` then `caplog.messages == ["quote CN-1"]` (typed `pytest.LogCaptureFixture`);
- `pytest.RaisesGroup(ValueError, TypeError)` over `ExceptionGroup("two", [ValueError("a"), TypeError("b")])`; `pytest.RaisesGroup(pytest.RaisesExc(ValueError, match="^a$"))`;
- `pytest.raises(OSError, check=lambda e: e.errno == 2)`;
- `pytest.warns(DeprecationWarning, match="old")`;
- `pytest.approx` accepts `Decimal` (`Decimal("0.1") + Decimal("0.2") == pytest.approx(Decimal("0.3"))`), not used by B because the book compares `Decimal` exactly.
- Reference page: `match` "is tested against the string representation of the exception and its PEP 678 __notes__ using re.search()"; `check` "Added in version 8.4. If specified, a callable that will be called with the exception as a parameter after checking the type and the match regex if specified."; `RaisesGroup` "Added in version 8.4. Contextmanager for checking for an expected ExceptionGroup."
- A function default `out: TextIO = sys.stdout` binds the stream at definition time, before `capsys` replaces `sys.stdout`; B's `write_quotes` takes `out: TextIO | None = None` and resolves `sys.stdout` at call time (the "default captured at definition" trap from "Seams in Python").

**P. Mocks on pytest-mock 3.17.0.** Probe member `mock_probe` (a `CarrierGateway` Protocol, a `Fastline` class, an async `confirm`), ten tests; mypy `--strict` clean:
- `mocker.spy(gw, "quote")`: the real result `Decimal("4.50")`, `spy.assert_called_once_with(Decimal("10"))`, `spy.spy_return == Decimal("4.50")`, `spy.spy_return_list == [Decimal("4.50")]`;
- autospec `gw.mock_calls == [mock.call.quote(Decimal("2")), mock.call.book("CN-1")]`, `gw.quote.call_args == mock.call(Decimal("2"))`, `gw.book.assert_called_once_with(mock.ANY)`;
- `side_effect = [Decimal("1"), TimeoutError("late")]`: the value, then the exception, then `StopIteration`;
- `mock.Mock().assret_called_once()` raises `AttributeError` matching `assret`;
- `mocker.seal(m)` then `m.book` raises `AttributeError`;
- `mocker.patch.dict(...)` and `mocker.patch.object(Fastline, "quote", autospec=True, return_value=Decimal("9"))` behave as documented;
- `mock.create_autospec(confirm)` returns a `function` whose `.mock` is an `AsyncMock`; its call returns a coroutine, and after `asyncio.run` `assert_awaited_once_with("CN-1")` passes;
- after `mocker.resetall()`, a `mocker.stub` keeps `call_count == 1` and an autospec's `quote.call_count == 0`;
- `with mocker.patch.object(Fastline, "book"):` warns `PytestMockWarning: Mocks returned by pytest-mock do not need to be used as context managers. The mocker fixture automatically undoes mocking at the end of a test. ...`, and under the root `filterwarnings = ["error"]` the test fails with `E   pytest_mock.plugin.PytestMockWarning: ...`;
- `reveal_type` under mypy 2.4.1: `mocker.patch(...)` and `mocker.patch.object(...)` and `mocker.create_autospec(..., instance=True)` are `unittest.mock.MagicMock | unittest.mock.AsyncMock | unittest.mock.NonCallableMagicMock`; `mocker.spy(...)` is `pytest_mock.plugin.SpyType`; `mocker.stub()` is `unittest.mock.MagicMock`; `mocker.Mock()` is `Any`; `g: CarrierGateway = mocker.stub()` passes.
- pytest-mock usage page: "The mocker.spy object acts exactly like the original method in all cases, except the spy also tracks function/method calls, return values and exceptions raised."; "spy_return_list: contains a list of all returned values of the spied function (new in 3.13)."; "Mocks created with mocker.stub(), mocker.async_stub() or mocker.Mock() and the other aliases are not tracked, so they are not reset."; "The purpose of this plugin is to make the use of context managers and function decorators for mocking unnecessary, so it will emit a warning when used as such."
- `unittest.mock` page (3.15.2): "unsafe: By default, accessing any attribute whose name starts with assert, assret, asert, aseert or assrt will raise an AttributeError."; "spec_set: A stricter variant of spec. If used, attempting to set or get an attribute on the mock that isn’t on the object passed as spec_set will raise an AttributeError."; "The basic principle is that you patch where an object is looked up, which is not necessarily the same place as where it is defined."

**Q. Mock census.** `grep -rlnE "mocker|unittest.mock|create_autospec|MagicMock|monkeypatch"` over `examples/*/tests` and `examples/*/src`:
- `mocker`/`unittest.mock`: ch06 `tests/test_dip.py` (`mocker.create_autospec(..., instance=True)`, `assert_called_once_with`); ch11 `tests/test_doubles.py` (`create_autospec`, `Mock()`, `Mock(spec=...)`, `return_value`, `side_effect`, `assert_called_once_with`, `assert_not_called`) and `tests/test_static.py` (`Mock`, `MagicMock`, `create_autospec` as mypy snippets); ch33 `tests/test_patching.py` (`mocker.patch`, `create=True`, `autospec=`, `mock.patch` as a context manager) and `tests/test_static.py` (`patch` as decorator and context manager, `MagicMock`).
- `monkeypatch` only: ch03 (`test_dissolve.py`, `test_disambiguate.py`), ch11 (`test_environment.py`), ch33 (`test_seams.py`, `test_patching.py`, `test_static.py`), ch34 (`tests/conftest.py`, the one namespace patch).
- `examples/*/src`: none. r19 decision 8 (no mocks in either member) and r16's single exception are the precedent. W2 writes `_plans/evidence/r20-mock-census.md` with the commands and per-file API lists.

**R. Sources, fetched 2026-11-07.** Quotable, exactly as on the page (W4a to W4c re-fetch each before quoting):
- uv projects/sync (https://docs.astral.sh/uv/concepts/projects/sync/): the exact and inexact sentences of evidence C and D; "If the lockfile is not up-to-date, uv will raise an error instead of updating the lockfile."
- uv workspaces (https://docs.astral.sh/uv/concepts/projects/workspaces/): "In a workspace, each package defines its own pyproject.toml, but the workspace shares a single lockfile, ensuring that the workspace operates with a consistent set of dependencies."
- uv projects/config (https://docs.astral.sh/uv/concepts/projects/config/): "The UV_PROJECT_ENVIRONMENT environment variable can be used to configure the project virtual environment path (.venv by default)."; "If a relative path is provided, it will be resolved relative to the workspace root."
- ruff configuration (https://docs.astral.sh/ruff/configuration/): "For each file, Ruff uses the "closest" config file in the directory hierarchy."; "In locating the "closest" pyproject.toml file for a given path, Ruff ignores any pyproject.toml files that lack a [tool.ruff] section."
- ruff settings (https://docs.astral.sh/ruff/settings/): `extend-select` "Unlike select, which replaces the default rule set when specified, extend-select adds to whatever rules are already active."
- ruff rules (https://docs.astral.sh/ruff/rules/): the default-rules sentence of evidence I.
- mypy command line (https://mypy.readthedocs.io/en/stable/command_line.html, 2.4.1): "This flag mode enables a defined subset of optional error-checking flags."; "Note: the --warn-unreachable flag is not automatically enabled by the strict flag."
- mypy config file (https://mypy.readthedocs.io/en/stable/config_file.html): "By default, mypy will discover configuration files by walking up the file system (up until the root of a repository or the root of the filesystem)."; "It is important to understand that there is no merging of configuration files, as it would lead to ambiguity."
- pytest API reference (https://docs.pytest.org/en/stable/reference/reference.html), configuration (https://docs.pytest.org/en/stable/reference/customize.html), import mechanisms (https://docs.pytest.org/en/stable/explanation/pythonpath.html), plugins (https://docs.pytest.org/en/stable/how-to/plugins.html): the sentences of evidence K to O.
- pytest-mock usage (https://pytest-mock.readthedocs.io/en/stable/usage.html): the sentences of evidence P.
- `unittest.mock` (https://docs.python.org/3/library/unittest.mock.html, "Python 3.15.2 documentation"): the sentences of evidence P.
- typeshed `stdlib/unittest/mock.pyi` (https://github.com/python/typeshed/blob/main/stdlib/unittest/mock.pyi): the comment ch11 quotes; C points to ch11 for it and may link the file.
- Not fetched at planning, for W4a to fetch or drop: uv's CLI reference page for `uv init` and `uv python install`, uv's default-groups sentence, mypy's "Integrating mypy into another Python application" (`mypy.api`).

**S. Repo facts.**
- **Reconciliation.** Rows run 1 to 248, so r20 adds 249 to 278. No legacy row (1 to 46) names an appendix. `CLAIMS_FIRST_ENFORCED = 47`. Ch cells are `41`, `42`, `43`, `41-43` and `0`.
- **Figures.** 41 entries; r20 adds none.
- **Test names.** None of the new names in the Example spec appears among the 915 existing `def test_` lines (grep at planning; W1b and W1c re-check). Existing names cited by B and C rows were each found exactly once: `test_a_plain_mock_passes_an_assertion_on_a_misspelled_method`, `test_spec_rejects_unknown_names_but_not_wrong_signatures`, `test_autospec_rejects_names_and_signatures`, `test_side_effect_drives_the_timeout_branch`, `test_mypy_accepts_every_mock_where_a_gateway_is_expected`, `test_book_best_books_only_the_winner`, `test_patch_refuses_a_name_the_module_does_not_have`, `test_unittest_mock_patch_follows_the_same_lookup_rule`, `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier`, `test_mypy_types_a_patch_as_a_magic_mock_or_as_its_replacement`, `test_monkeypatch_undoes_its_changes_when_the_context_ends`, `test_monkeypatch_refuses_a_misspelt_name`, `test_monkeypatch_with_raising_false_creates_a_name_nothing_reads`, `test_validity_reads_the_environment_and_the_context_restores_it`, `test_autospec_enforces_the_protocol_shape_at_runtime`, `test_autospec_bypasses_mypy`, `test_autospec_refuses_a_call_with_the_wrong_signature` (ch33; C's names avoid it).
- **Members.** No member uses project `pytest-reference` or `mocking-reference`, or package `pytest_reference` or `mocking_reference`.
- **Promises the appendices must honour** (grep of `_docs/`, `_parts/`, `_examples/`, `README.md`, `index.html`, `bibliography.html`, the example READMEs for the three titles, the three slugs and "Appendix"):
  1. "Proving it works: pytest, pytest-mock, and mypy", fixtures section: "Brian Okken's *Python Testing with pytest* ... is the book-length treatment of fixtures, parametrization and configuration, and the fixtures how-to is the primary source for what follows. The chapter titled pytest reference lists the rest." B must list the rest of fixtures, parametrization and configuration.
  2. The same chapter, doubles section: "The chapter titled Mocking reference: unittest.mock and pytest-mock lists the rest of the mock API, and the standard library's autospeccing section is the source for what `create_autospec` copies." C must list the mock API beyond `Mock`, `Mock(spec=...)`, `create_autospec`, `return_value`, `side_effect`, `assert_called_once_with` and `assert_not_called`.
  3. "Seams in Python: monkeypatch, injection, and duck typing", "monkeypatch or mock.patch": "`mocker.patch` from pytest-mock takes the same string targets ... and the API is collected under Mocking reference: unittest.mock and pytest-mock." C must collect the patch API (`mocker.patch` and its `autospec=`, `create=`, `patch.object`, `patch.dict`, `mocker.stop`, `unittest.mock.patch` as decorator and context manager) and point to the `monkeypatch` rows in B.
  4. Part 14's blurb (header).
  5. Domain rows A ("Commands used across the book"; `uv`, `ruff`, `mypy --strict`), B ("Fixtures and parametrisation used in the examples"; `pytest`) and C ("Autospec and patch targets on `CarrierGateway`"; `mocker`, `create_autospec`). C's member uses `CarrierGateway`.
  6. CLAUDE.md, "Example code": "Prefer `mocker.create_autospec` and say in the prose that mocks bypass the static check." C says it once.
  7. Not a promise to these appendices: ch11 points to "xUnit test patterns (Meszaros)" (r21), and `bibliography.html`'s Meszaros row names "the test-double reference appendix" (r21). r20 doesn't describe Appendix D; C doesn't point to it (lesson "Pointers").
  8. "Prerequisites and the toolchain" has no link to A. A points to it; ch00 isn't edited except decision 6's sentence.
- **Exact titles for pointers** (front matter): "Prerequisites and the toolchain"; "Proving it works: pytest, pytest-mock, and mypy"; "ISP, DIP, and dependency injection without a framework"; "Seams in Python: monkeypatch, injection, and duck typing"; "Dependency-breaking techniques for modern Python"; "Protocol, duck typing, and structural typing with mypy"; "The GIL and performance"; "Final project" (fixtures in place of conftest imports); "pytest reference"; "Mocking reference: unittest.mock and pytest-mock"; "Build and toolchain reference: uv, ruff, mypy".
- **Overlap.** ch00 owns install, clone, the one-time sync, check-prereqs, the four gates in order, running one example, pin bumping and troubleshooting; A doesn't repeat them and points there. ch11 owns the claim-witness method, the four-doubles table, `assert_type`, the typed-ignore regression, and the strict configuration experiments; B and C point there. ch33 owns "patch where the name is looked up" and its tests; C states the rule in one sentence with the docs quote and cites ch33's tests.
- **CI.** The `free-threaded` job runs `examples/37-*` and `examples/38-*` only. The `validate` job runs `uv run --locked python scripts/validate.py`.

**T. Not claimable.** That a feature is "best practice" or "recommended" beyond a quoted doc sentence; performance of any tool (no timings in reader text beyond a quoted pytest summary line); that ruff's or uv's unversioned docs describe 0.17.4 or 0.13.7 (the recorded run is the version witness; where the page and the run disagree, the run wins and the page isn't quoted); `pytest.approx` behaviour beyond evidence O (B doesn't use it); behaviour of `mocker` fixtures of other scopes (`class_mocker` and the rest are named only as the usage page lists them, if at all); `unittest.mock` behaviour on other Python versions; the hazard of `uv init` inside a git checkout beyond what W1a records.

## What is new in each appendix

**A (toolchain reference).**
- One table per tool of the commands and options the book uses, each with what it does on the pinned version and a witness.
- The traps: exact sync without `--all-packages`; a member table shadows the root; mypy's duplicate module; ruff's `select` replacing a broad default set; `.venv-ft` outside a git checkout; `uv init`'s defaults.
- The free-threaded environment from the same lockfile.

**B (pytest reference).**
- The root configuration line by line, and pytest 9's `strict` and `[tool.pytest]`.
- `--import-mode=importlib` and what it means for `conftest.py` and shared helpers.
- Fixtures, parametrize, built-in fixtures, exception and warning assertions, command-line options: each row with a test.

**C (mocking reference).**
- The book's order of preference and the census of where mocks appear.
- Making, configuring and inspecting doubles; patching through `mocker`; spies, stubs and `resetall`; async doubles; what mypy sees.

## Approach

- **Thesis wording.**
  - A: three tools read settings from the first file they find and never merge two; the root `pyproject.toml` is that file for every member, and each command in the book is the same command from the root or a member once the root sync has run.
  - B: the suites rely on a small set of pytest features and on configuration that turns silence into failure; each row here is shown by a test on pytest 9.2.0.
  - C: the book reaches for a mock last, and when it does, it uses the mock that checks the most; this is the API it uses and the rest a reader will meet, each row shown by a test on pytest-mock 3.17.0 and Python 3.15.2.
- **Members** (B, C), standalone, named after the package, no `[tool.*]` table, created with `uv init --lib --vcs none --no-readme --no-description --author-from none --name <project> examples/<slug>` and then edited to the repo's `requires-python = ">=3.15"` and `uv_build>=0.13.7,<0.14` (evidence F).
- **Per-row witnesses.** Every command, flag, option, fixture, function, attribute and assertion method an appendix names appears in that appendix's witness table below with exactly one of: a test name (new or existing), a line of `_plans/evidence/r20-toolchain-runs.md`, or a fetched source URL linked in the appendix. W4a to W4c hand back the table filled with the observed witness for every row, and add rows for anything their prose names that the table lacks; an item without a witness is cut.
- **Static witnesses.** Copy `_run`/`_codes` from `examples/38-asyncio-and-the-patterns/tests/test_static.py`. Each static test asserts exit status, an exact sorted code list or exact `reveal_type` substrings, never a line number, and names its credited thing and a mutation that fails it.
- **pytester tests.** Each builds its inner project with `makepyfile`, `makepyprojecttoml` or explicit files, runs `runpytest(...)` in-process, and asserts `assert_outcomes(...)` with exact counts plus at most one `fnmatch_lines` pattern that holds no path. Inner configuration is written explicitly in each test, so no outer option leaks in (evidence K).
- **Negative witness rule.** Every pinned behaviour in `src` and every pytester claim has a deletion row or a mutation that makes its test fail.
- **Determinism.** No clock, `random`, sleep or network; lists and tuples only in failing assertions; no assertion names a path or an address; `pytester` output is never compared to a path.
- **Counts** come from the code; the pytest summary line wins.
- **Repair rule (r12).** After every repair the validator re-reads the paragraph and the rows that depend on it.

Rejected in either member's `src`: `monkeypatch`, `mock`, `patch`, `Any`, `cast`, `Optional`, `random`, `global`, `sys.modules`, `time.`, `datetime`, `print(`, `exec(`, `eval(`, `subprocess`, `socket`, `urllib`, `http`. In B's `tests`, `subprocess` appears only in `test_static.py`'s mypy helper if it needs one (mypy is reached through `mypy.api`, so expect none). In C's `tests`, mocks are the subject.

## Per-appendix spec

Common to all three: front matter keeps `layout`, `order`, `part`, `appendix`; `description` is rewritten from "Draft pending" (W0 writes a one-sentence draft, W4 finalises). Spine headings exactly `## Learning objectives`, `## Why this matters`, `## For deeper coverage`; `## Reference` is removed. No `## What you can do now` (not in the appendix spine); the objectives map to sections by their order. No figure, no sidebar, no experiment. Links to other book pages use `{{ '/docs/<slug>/' | relative_url }}`.

### Appendix A: Build and toolchain reference: uv, ruff, mypy

Sections (about 2,000 prose words, max 2,500; at most six excerpts):

1. `## Learning objectives` (~80), four bullets: find the uv, ruff or mypy command for a task and what it does on the pinned version; say which file each tool reads and why a member carries no tool table; build and use the free-threaded environment; add a member and bump a pin without breaking `--locked`.
2. `## Why this matters` (~150). Intent first: three tools, three discovery rules, one root file. Quote mypy's "there is no merging of configuration files" sentence and ruff's "closest" sentence; pytest's "first match wins" is B's. One sentence that the install, sync and gate walkthrough is in "Prerequisites and the toolchain" and isn't repeated. One sentence naming the pinned versions this page describes (uv 0.13.7, ruff 0.17.4, mypy 2.4.1) and that the version table lives in that chapter.
3. `## uv: interpreter, environment and lockfile` (~400 plus a table). Table: command | what it does here | used in. Rows: `uv python install 3.15.2`; `uv python install 3.15.2t`; `uv python list --only-installed`; `uv sync --locked --all-packages`; `uv lock`; `uv lock --check`; `uv lock --upgrade-package <name>`; `uv run <command>` (from the root or a member); `uv run --locked` (the CI book-check job). Prose: exact against inexact sync with the 52-to-13 run and the `consignments` import error (evidence C; quote the sync page's "exact" sentence); the member run before the root sync (evidence D); `--locked` and `--check` with the two-line message as an excerpt (evidence E). The root's `package = false`, `default-groups = ["dev"]` and `members = ["examples/*", "spikes/*"]` in one sentence each with the workspaces quote.
4. `## Adding a member` (~200). The `uv init` command of the Approach, what it creates (three files), the two edits to match the repo, and the defaults it would otherwise write (a git identity in `authors`, a README, a description, a nested repository outside a git checkout; evidence F); then `uv lock`. Excerpt: the resulting `pyproject.toml` after the edits (as the W1b member has it).
5. `## The free-threaded environment` (~200). The three commands of the CI job (excerpt the three `run:` lines; none contains `{{`), the `UV_PROJECT_ENVIRONMENT` quote and the relative-path sentence, `sys._is_gil_enabled()` `False` against `True` (evidence J), and `.venv-ft` in `extend-exclude` with the reason (evidence I, decision 7). One pointer to "The GIL and performance" by title for why the job exists, describing nothing further.
6. `## ruff: lint and format` (~400 plus two tables). Table 1: prefix | linter (the ten of the root's `select`, names from `ruff linter`). Table 2: command | what it does: `ruff check .`, `ruff check --fix`, `ruff check --diff`, `ruff check --statistics`, `ruff check --output-format concise`, `ruff check --show-settings <file>`, `ruff check --isolated`, `ruff rule <CODE>`, `ruff linter`, `ruff format`, `ruff format --check`. Prose: the root `select` replaces ruff 0.17.4's default set (279 against 407 rules, exact counts from W1a; quote the `extend-select` sentence), `line-length = 100`, `target-version = "py315"`, `quote-style = "double"`; `# noqa: CODE` and `RUF100` for an unused one (evidence I). Excerpt: the root `[tool.ruff]`, `[tool.ruff.lint]` and `[tool.ruff.format]` tables as they stand after W0.
7. `## mypy: strict types` (~400 plus a table). Table: the thirteen flags `--strict` enables on 2.4.1, with a short gloss each; `--warn-unreachable` as the one the root adds; `--warn-redundant-casts` already in the list (decision 10). Prose: quote the two command-line sentences; per-member runs and the duplicate-module message as an excerpt (first line, scrubbed; evidence H); the root `[tool.mypy]` and its `overrides` table (excerpt); `--enable-error-code deprecated` as the example of an error code outside `--strict` (evidence H); `mypy.api.run`, `reveal_type`, `assert_type` and typed `# type: ignore[code]` as one sentence each pointing to "Proving it works: pytest, pytest-mock, and mypy".
8. `## verify.sh and CI` (~150). The script's steps in order (sync, ruff check, ruff format check, mypy per member, mypy on scripts, pytest), each mapping to a table above; CI runs the same script, plus the book checks and the free-threaded job, and one summary check gates a merge. No `host_ids.py` in any command (lesson "Reader commands").
9. `## For deeper coverage` (~100): uv projects/sync, workspaces and config; ruff configuration, settings and rules; mypy command line and configuration file; "Prerequisites and the toolchain" by title; the bibliography link.

Also, W4a rewrites ch00's `--all-packages` sentence (decision 6) and nothing else in ch00.

**Witness table A.** "run" means a line of `_plans/evidence/r20-toolchain-runs.md` (W1a records the command, exit status and quoted lines); "src" means a source URL linked in A.

| Item | What A says | Witness |
| --- | --- | --- |
| `uv python install 3.15.2` / `3.15.2t` | installs the pinned default and free-threaded builds into uv's store | run (`uv python list --only-installed` after; no-op when present); src uv CLI reference (W4a fetches) |
| `uv python list --only-installed` | lists installed interpreters | run (help line; paths scrubbed) |
| `uv sync --locked --all-packages` | dev tools plus every member in one `.venv` | run (52 distributions); src sync |
| `uv sync --locked` without `--all-packages` | exact sync removes the members; collection fails | run (13 distributions, `ModuleNotFoundError`); src sync |
| `--locked` | refuses a lockfile that would change | run (help line, message, exit 1); src sync |
| `--frozen` (named only if stated) | uses the lockfile without checking it | run (help line); src sync |
| `uv lock` | writes the resolution after a pin edit | run |
| `uv lock --check` | exit 0 when current; the quoted error otherwise | run |
| `uv lock --upgrade-package <name>` | lets one package move | run (help line only; no upgrade is performed) |
| `uv run` from a member | before the root sync: member only, no pytest; after: the root `.venv`, inexact | run (both); src sync |
| `uv run --locked` | used by CI's book checks | `ci.yml`; run (help line) |
| `package = false`, `default-groups`, workspace `members` | the virtual root, the dev group installed by default, the member glob | root `pyproject.toml`; src workspaces; run (`uv init` "already a member" line) |
| `uv init --lib --vcs none --no-readme --no-description --author-from none --name` | the three files; root unchanged; defaults otherwise | run (both forms) |
| `UV_PROJECT_ENVIRONMENT=.venv-ft`, `--python 3.15.2t` | second environment, same lockfile; GIL off | run (`False 1`); src config; `ci.yml` |
| `.venv-ft` in `extend-exclude` | ruff lints it outside a git checkout without the line | run (before and after, in a copy without `.git`) |
| member `[tool.*]` tables | replace the root's for that member, for all three tools | run (mypy, pytest, ruff `line-length`); src mypy config file, ruff configuration; B row for pytest |
| ruff prefixes | the ten linter names | run (`ruff linter`) |
| root `select` vs defaults | 279 against 407 rules on 0.17.4 | run (`--show-settings` counts); src settings, rules |
| `ruff check` options listed in table 2 | each one's help line | run |
| `ruff rule <CODE>` | prints a rule's page | run (`ruff rule UP045`) |
| `ruff format`, `--check` | formats; reports without writing | run; `verify.sh` |
| `# noqa: CODE`, `RUF100` | an unused suppression is itself a finding | run |
| `--strict` flag list | thirteen flags, verbatim | run (`mypy --help`); src command line |
| `warn_unreachable`, `warn_redundant_casts` | the first added by the root, the second already in strict | run; src command line |
| root config applies from a member | strict and unreachable without flags | run (evidence H) |
| duplicate module | message from the root; per-member runs pass | run; `verify.sh` |
| `[[tool.mypy.overrides]] ignore_errors` | vendored scripts | root `pyproject.toml`; src config file |
| `--enable-error-code deprecated` | an optional code, off under strict | run |
| `--python-version`, `--cache-dir`, `--no-incremental` (named only if stated) | help lines | run |
| `verify.sh` steps | order as in the script | `scripts/verify.sh` (excerpt or list matches the file) |
| ch00's corrected sentence | `--all-packages` installs the members | row 278 |

### Appendix B: pytest reference

Sections (about 2,100 prose words, max 2,500; at most six excerpts):

1. `## Learning objectives` (~80), five bullets: read the root `[tool.pytest.ini_options]` and say what each line refuses; say what `--import-mode=importlib` allows and forbids; pick the fixture form for a dependency, a cleanup, a scope or an indirect parameter; assert an exception, an exception group or a warning precisely; select and rerun tests from the command line.
2. `## Why this matters` (~150). Intent first: most of what a suite proves depends on a few configuration lines and fixture rules that fail silently when misread. One sentence pointing to "Proving it works: pytest, pytest-mock, and mypy" for the method and the experiments, not repeated; one sentence that every row below is a test in `examples/42-appendix-b-pytest` or an existing test named in the row.
3. `## The root configuration` (~350). Excerpt the root `[tool.pytest.ini_options]` table. Each line with its test: `--strict-markers` (21), `--strict-config` (23), `xfail_strict = true` and its 9.0 name `strict_xfail` (22; quote the rename sentence), `filterwarnings = ["error"]` (24), `testpaths`, `--import-mode=importlib` (next section). pytest 9's `strict` umbrella (25; quote its list) and the native `[tool.pytest]` table (quote the two configuration-page sentences), with one sentence that the repo keeps the INI-style table (decision 8). "the first match wins" (26; quote).
4. `## Import mode and conftest.py` (~350). The collision under prepend and the two runs under importlib (27, 28; quote the importlib and unique-name sentences, stopping before the en dash); a test module can't import `conftest` (29; quote "Test modules can’t import each other."). Consequence in the book: shared values reach tests through fixtures, and conftest types are imported under `TYPE_CHECKING` (pointer to "Final project" by title, describing nothing further). `pytest_plugins` in a member's conftest breaks the root collection (30; quote the plugins-page note); this member loads `pytester` from its test modules. Excerpt test 27.
5. `## Fixtures` (~350 plus a table). Table: form | what it gives | test. Rows: injection by name and `conftest.py` visibility (existing ch11 fixture use, `test_book_best_books_the_winner_and_returns_its_reference`); `yield` teardown, also after a failing test (`run: _plans/evidence/yield-fixture-teardown-on-failure.md` is the existing record; row 264 cites test 1 for order); scope and teardown order (1, 2); factory fixture (3); `autouse=True` (4); `@pytest.mark.usefixtures` (5); `params=` and `request.param`, and `indirect=True` (6); `request.getfixturevalue` (7). Excerpt test 1.
6. `## Parametrize` (~200 plus a table). `pytest.param(..., id=...)` (8), `pytest.param(..., marks=...)` (9), stacked decorators multiply (10), duplicate ids get a numeric suffix unless `strict_parametrization_ids` (11; quote).
7. `## Built-in fixtures` (~250 plus a table). `tmp_path` (12), `capsys` (13; the call-time `sys.stdout` note of evidence O), `caplog` (14), `monkeypatch` (`setattr`, `setenv`, `delenv`, `context()`, `raising=False`: existing ch11 and ch33 tests, one row each), `pytester` (this member's configuration tests). Type annotations for each (`pytest.TempPathFactory` not needed; `pathlib.Path`, `pytest.CaptureFixture[str]`, `pytest.LogCaptureFixture`, `pytest.MonkeyPatch`, `pytest.Pytester`), with test 37.
8. `## Exceptions and warnings` (~250). `pytest.raises(..., match=...)` is `re.search` (17; quote), `check=` (18; quote), `pytest.RaisesGroup` and `pytest.RaisesExc` against `rate_batch`'s group (19; quote), `pytest.warns(..., match=...)` (20; existing ch09 and ch38 tests too). Excerpt test 19.
9. `## Command-line options` (~200 plus a table). `-q`, `-v`, `-x`, `-k`, `-m`, `--lf`, `--co`, `-o name=value`, `-s`, `--tb=short`, `-p`; each with its test (31 to 36) or its help line in the run file (`-q`, `-v`, `-s`, `--tb`, `-p`).
10. `## Running the reference tests` (~60). From the root once `uv sync --locked --all-packages`; then `cd examples/42-appendix-b-pytest`, `uv run pytest -q`, `uv run mypy --strict src tests`. At most the final summary line quoted, from a fresh scrubbed run.
11. `## For deeper coverage` (~100): the four pytest pages; Okken's *Python Testing with pytest*, second edition (Pragmatic Bookshelf, 2022); "Proving it works: pytest, pytest-mock, and mypy" and "Mocking reference: unittest.mock and pytest-mock" by title; the bibliography link.

**Witness table B.** New tests are numbered as in the Example spec; "existing" names a test outside the member.

| Item | What B says | Witness |
| --- | --- | --- |
| `--strict-markers` | an unregistered marker stops collection | 21; src reference |
| `--strict-config` | a configuration warning is an error | 23; src reference |
| `xfail_strict` / `strict_xfail` | a passing `xfail` fails the run; both names work | 22 (parametrised over both names); src reference |
| `filterwarnings = ["error"]` | a warning becomes a failing test; without it, a summary line | 24; src reference |
| `strict = true` | enables the four options | 25 (one case per option); src reference |
| `[tool.pytest]` vs `[tool.pytest.ini_options]` | both read by pytest 9; the repo uses the second | src customize; root `pyproject.toml` |
| first config file wins | a member's table replaces the root's | 26; src customize; run (evidence G) |
| `testpaths` | where a bare `pytest` from the root looks | root config; src reference |
| `--import-mode` prepend vs importlib | collision vs two passes | 27, 28; src pythonpath |
| importlib and `conftest` imports | `ModuleNotFoundError` | 29; src pythonpath |
| `pytest_plugins` placement | member conftest breaks root collection; a test module works | 30; `run: W1b` (the member collects from both directories); src plugins |
| yield fixture, scope, teardown order | reverse of setup; module scope set up once | 1, 2; existing `yield-fixture-teardown-on-failure` evidence |
| factory, autouse, usefixtures, params, indirect, getfixturevalue | as in the table | 3 to 7 |
| `pytest.param` id and marks, stacked parametrize | ids in node ids; a per-case mark; cross product | 8 to 10 |
| duplicate ids, `strict_parametrization_ids` | suffixes, or an error | 11; src reference |
| `tmp_path`, `capsys`, `caplog` | per-test directory; captured output; captured records | 12 to 14 |
| `monkeypatch` methods | set, delete, restore, refuse a missing name | existing: `test_validity_reads_the_environment_and_the_context_restores_it`, `test_monkeypatch_refuses_a_misspelt_name`, `test_monkeypatch_with_raising_false_creates_a_name_nothing_reads`, `test_monkeypatch_undoes_its_changes_when_the_context_ends` |
| fixture type annotations | mypy checks a use of a typed fixture | 37 |
| `raises(match=)`, `check=`, `RaisesGroup`, `RaisesExc`, `warns(match=)` | as in the section | 17 to 20; src reference |
| `-k`, `-m`, `-x`, `--lf`, `--co`, `-o` | selection and reruns | 31 to 36; run (help lines) |
| `-q`, `-v`, `-s`, `--tb`, `-p` | help lines only | run |

### Appendix C: Mocking reference: unittest.mock and pytest-mock

Sections (about 2,100 prose words, max 2,500; at most six excerpts):

1. `## Learning objectives` (~80), five bullets: say when the book uses a mock and which one; build a double that refuses the names and calls its target refuses; configure and inspect calls without asserting less than you meant; patch through `mocker` and know what it undoes; read what mypy does and doesn't check about a mock.
2. `## Why this matters` (~200). Intent first: a mock is assignable to every type, so the type checker has nothing to check at the call site (one sentence, pointing to "Proving it works: pytest, pytest-mock, and mypy" for the typeshed comment); every check a mock makes is one you asked for. The book's order of preference (decision 3), one sentence each with its pointer: a fake through a parameter ("ISP, DIP, and dependency injection without a framework"), `create_autospec` where the calls are the claim ("Proving it works..."), a patch only where no parameter exists ("Seams in Python..." and "Dependency-breaking techniques for modern Python").
3. `## Where the book uses mocks` (~120 plus a table). The census (evidence Q): chapter title | API | test. Rows for ch06, ch11, ch33 (mocks) and a line for the `monkeypatch`-only chapters; `src` uses none. Witness `run: _plans/evidence/r20-mock-census.md`.
4. `## Making a double` (~300 plus a table). Table: form | refuses an unknown name | refuses a wrong call | mypy | test. Rows: `Mock()` (existing ch11), `Mock(spec=...)` (existing ch11), `Mock(spec_set=...)` (1), `create_autospec(..., instance=True)` (existing ch11, ch06), `seal` (2), `MagicMock`, `AsyncMock` (20), `wraps=` (6). Prose: the assert-typo refusal and `unsafe` (3; quote); `mocker.Mock` and the other aliases (quote the usage page's alias list in prose, not a copy of it).
5. `## Configuring and inspecting calls` (~350 plus a table). `return_value` and `side_effect` as an exception (existing ch11), an iterable (4), a callable (5); `called`, `call_count`, `call_args`, `call_args_list` and `ANY` (8), `mock_calls` and `call` (7), `assert_called_once_with`, `assert_not_called` (existing ch11), `assert_has_calls` (9), `assert_any_call` (8 if used), `reset_mock(return_value=..., side_effect=...)` (10). Prose: ch11's "asserting that a mock was called, not what happened" habit by pointer; assert the result before the calls. Excerpt test 7.
6. `## Patching with mocker` (~350). Quote the "patch where an object is looked up" sentence; cite ch33's tests for the rule and for `create=` and `autospec=` (existing). `mocker.patch.object` with `autospec=True` (11), `mocker.patch.dict` (12), `mocker.stop` (13), undone at the end of the test (12's second half). The context-manager warning and why the root filter makes it a failure (14; quote the usage page's purpose sentence); `unittest.mock.patch` as decorator and context manager, for code outside pytest, with ch33's static test for how mypy types it (existing). Excerpt test 14.
7. `## Spies and stubs` (~250). `mocker.spy` keeps behaviour and records `spy_return`, `spy_return_list` (15) and `spy_exception` (16); `mocker.stub` for a callback (17); `mocker.resetall` resets patches, spies and autospecs, not stubs or `mocker.Mock` (18; quote). Excerpt test 18.
8. `## Async doubles` (~150). `create_autospec` of an `async def` returns a function whose call is a coroutine, and `assert_awaited_once_with` checks the await (19); `AsyncMock` with a `return_value` (20). Excerpt test 19.
9. `## What mypy sees` (~150). `reveal_type` of `mocker.patch`, `mocker.spy`, `mocker.stub` and `mocker.Mock()` (22; exact strings of evidence P); a stub passes where a `Notify` callback is expected while a hand-written callback of the wrong shape is refused (23). Annotate with `MockerFixture`. Say once that a mock bypasses the static check.
10. `## Running the reference tests` (~60), as in B, for `examples/43-appendix-c-mocking`.
11. `## For deeper coverage` (~100): the `unittest.mock` page and its "getting started" companion if W4c fetches it, pytest-mock's usage page, typeshed's `mock.pyi`, Fowler's "Mocks Aren't Stubs" (title and topic), Meszaros's *xUnit Test Patterns* for the double names (bibliography), "Proving it works..." and "Seams in Python..." by title, the bibliography link.

**Witness table C.**

| Item | What C says | Witness |
| --- | --- | --- |
| order of preference and census | where and why the book mocks | `run: _plans/evidence/r20-mock-census.md`; existing `test_book_best_books_only_the_winner`, `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier` |
| `Mock()`, `spec=`, `create_autospec(..., instance=True)` | accepts anything; refuses names; refuses names and signatures | existing `test_a_plain_mock_passes_an_assertion_on_a_misspelled_method`, `test_spec_rejects_unknown_names_but_not_wrong_signatures`, `test_autospec_rejects_names_and_signatures`, `test_autospec_enforces_the_protocol_shape_at_runtime` |
| `spec_set=` | refuses setting an unknown name | 1; src unittest.mock |
| `seal` | no new attributes after sealing | 2 |
| assert typo, `unsafe` | `assret_*` raises | 3; src unittest.mock |
| `side_effect` iterable, callable | values in order then `StopIteration`; computed returns | 4, 5; existing `test_side_effect_drives_the_timeout_branch` for the exception form |
| `wraps=` | calls pass through to the real object | 6; src unittest.mock |
| `mock_calls`, `call` | every call, in order | 7 |
| `call_args`, `call_args_list`, `ANY` | last call, all calls, a wildcard | 8 |
| `assert_has_calls` | an ordered run of calls | 9 |
| `reset_mock` | clears calls; keeps configuration unless asked | 10; src unittest.mock |
| `mocker.patch` string target, `create=`, `autospec=` | lookup rule; refusal of a missing name; signature check | existing `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier`, `test_patch_refuses_a_name_the_module_does_not_have`, `test_autospec_refuses_a_call_with_the_wrong_signature`; src unittest.mock |
| `mocker.patch.object`, `mocker.patch.dict`, `mocker.stop` | replace an attribute; restore a mapping; undo one patch | 11 to 13 |
| `mocker.patch` as a context manager | warns; fails under the root filter | 14; src pytest-mock usage |
| `unittest.mock.patch` decorator and context manager | same lookup rule; how mypy types it | existing `test_unittest_mock_patch_follows_the_same_lookup_rule`, `test_mypy_types_a_patch_as_a_magic_mock_or_as_its_replacement` |
| `mocker.spy` and its attributes | real behaviour plus records | 15, 16; src pytest-mock usage |
| `mocker.stub` | records a callback | 17 |
| `mocker.resetall` scope | not stubs or aliases | 18; src pytest-mock usage |
| async autospec, `AsyncMock`, `assert_awaited_once_with` | coroutine on call; await recorded | 19, 20 |
| `reveal_type` results; stub where a callback is expected | exact strings; accepted vs refused | 22, 23; existing `test_mypy_accepts_every_mock_where_a_gateway_is_expected`; src typeshed |

Citations, all three: verify each before writing; quote no sentence unless checked on a fetched page; stop each quotation where the page's sentence stops, and before any dash; keep curly apostrophes or stop before them; no outcome claim; no comparison between languages.

## Example spec

### Appendix A evidence: `_plans/evidence/r20-toolchain-runs.md` (W1a)

A dated file, written in a fresh scratch copy (no `.git`, no `.venv`, `uv sync --locked --all-packages`), then a second copy for the before-sync row, both deleted afterwards. One section per row of witness table A: the exact command (relative to the repo root), the exit status, and the quoted lines (help lines verbatim, messages verbatim, counts), scrubbed with `python3 scripts/host_ids.py filter` (paths become `<repo>` or `~`). It states the versions it ran on and that the counts are those of this repository at this commit. It records the ruff `.venv-ft` row before and after W0's config line, both in a copy without `.git`. No `uv python install` that downloads anything (the interpreters are present; a download would be a host change only in the user's store, but none is needed).

### `examples/42-appendix-b-pytest` (project `pytest-reference`, package `pytest_reference`)

`pyproject.toml` in the r19 shape (`requires-python = ">=3.15"`, `uv_build>=0.13.7,<0.14`, no `[tool.*]`), created by the Approach's `uv init` command and edited.

- **`domain.py`**: `ConsignmentId` (`NewType`); frozen slotted `Weight(kilograms: Decimal)` refusing a non-positive weight (`ValueError`); `Consignment(id, zone, weight)`.
- **`rating.py`**: `RATES` (read-only `frozendict`, `EU` 0.45, `ASIA` 1.20, illustrative); `CENT`; `MAX_KILOGRAMS` (illustrative); `RatingError(LookupError)` for an unknown zone; `OverweightError(ValueError)` above the maximum; `quote(consignment, /) -> Decimal` (half up; logs `"quoted %s at %s"` at INFO on `logging.getLogger(__name__)`); `rate_batch(consignments, /) -> list[Decimal]` raising one `ExceptionGroup` of every `RatingError` and `OverweightError`; `legacy_quote` decorated with `@warnings.deprecated("use quote")`.
- **`report.py`**: `write_quotes(quotes: Mapping[ConsignmentId, Decimal], /, *, out: TextIO | None = None) -> None`, one line per consignment, `sys.stdout` resolved at call time (evidence O).
- `py.typed`, and an `__init__.py` that imports nothing.

`tests/conftest.py`: fixtures `consignment` (`CN-1`, `EU`, 10 kg), `make_consignment` (factory), an `autouse` fixture that records it ran in a list the autouse test reads, and `rated` (indirect: a zone name to a `Consignment`). `pytest_plugins` never appears in a conftest (decision 11).

`test_fixtures.py` (`pytest_plugins = ["pytester"]` after the imports):
1. `test_yield_fixtures_tear_down_in_reverse_order_of_setup` (pytester; the inner tests append to a file the outer test reads after the run: setup outer, setup inner, teardown inner, ..., teardown outer).
2. `test_a_module_scoped_fixture_is_set_up_once_for_the_module` (pytester; two inner tests, one setup line).
3. `test_a_factory_fixture_builds_a_fresh_object_per_call`.
4. `test_an_autouse_fixture_runs_without_being_named`.
5. `test_usefixtures_applies_a_fixture_whose_value_is_unused`.
6. `test_an_indirect_parameter_reaches_the_fixture_as_request_param` x (`EU`, `ASIA`) = 2.
7. `test_getfixturevalue_resolves_a_fixture_by_name`.

`test_parametrize.py` (pytester where ids are read from `--co -q`):
8. `test_pytest_param_ids_name_the_cases`.
9. `test_a_case_can_carry_its_own_mark` (a `pytest.param(..., marks=pytest.mark.xfail(strict=True, raises=RatingError))` case among passing cases).
10. `test_stacked_parametrize_takes_the_cross_product` (pytester: 2 x 3 = 6 collected).
11. `test_duplicate_ids_get_a_suffix_unless_strict_parametrization_ids` (pytester: suffixed ids, then a collection error with the option).

`test_builtin_fixtures.py`:
12. `test_tmp_path_is_a_fresh_directory_per_test` (pytester: two inner tests see different empty directories).
13. `test_capsys_captures_what_the_report_writes`.
14. `test_caplog_records_the_quote_message`.

`test_raises.py`:
17. `test_raises_match_is_a_regex_search` (a pattern without anchors matches inside the message; one with `^...$` against a longer message fails, shown with a nested `pytest.raises(AssertionError)` or through pytester: executor's choice, stated in the docstring).
18. `test_raises_check_tests_the_exception_object`.
19. `test_raises_group_matches_the_batch_failures` (`RaisesGroup(RatingError, OverweightError)` over `rate_batch`; `RaisesExc` with `match=`).
20. `test_warns_matches_the_deprecation` (`legacy_quote`).

`test_config.py` (pytester; each writes its inner `pyproject.toml` with `makepyprojecttoml`):
21. `test_an_unregistered_marker_fails_collection_under_strict_markers`.
22. `test_a_passing_xfail_fails_the_run_under_strict_xfail` x (`xfail_strict`, `strict_xfail`) = 2.
23. `test_an_unknown_option_fails_under_strict_config`.
24. `test_filterwarnings_error_turns_a_warning_into_a_failure` (with and without the line: `failed=1` against `passed=1, warnings=1`).
25. `test_strict_enables_the_four_strictness_options` x 4 (one inner project per option, `strict = true` and no individual option).
26. `test_the_first_config_file_wins_and_is_not_merged` (an inner root with `--strict-markers` and a subdirectory with its own `[tool.pytest.ini_options]`; run from the subdirectory, the unregistered marker passes with a warning).

`test_import_modes.py` (pytester):
27. `test_same_basename_test_files_collide_under_prepend`.
28. `test_importlib_mode_gives_each_test_file_a_unique_name`.
29. `test_importlib_mode_cannot_import_conftest_by_name`.
30. `test_pytest_plugins_in_a_non_root_conftest_fails_collection` (inner root, a `sub/conftest.py` with `pytest_plugins`, collection from the inner root fails with the deprecation message; executor check that the inner run reproduces evidence M).

`test_cli.py` (pytester):
31. `test_k_selects_by_name_expression`.
32. `test_m_selects_by_marker` (marker registered in the inner config).
33. `test_x_stops_at_the_first_failure` (the failing test first; the later test doesn't run).
34. `test_lf_reruns_only_the_last_failures`.
35. `test_collect_only_lists_without_running`.
36. `test_o_overrides_an_ini_option` (`-o xfail_strict=false` turns the strict failure back into `xpassed=1`).

`test_static.py`:
37. `test_mypy_checks_a_typed_fixture_use`: a snippet with `capsys: pytest.CaptureFixture[str]` doing `capsys.readouterr().out + 1` gives `["operator"]`; the same with `.out + "!"` gives `[]`. Credits the fixture annotation. Mutation: annotate `capsys: object` and the snippet reports `attr-defined` (executor quotes the line).

Planned: 35 test functions and 43 cases (6 and 22 parametrised as listed, 25 x 4; the rest single). Numbers 15 and 16 are unused (the `monkeypatch` rows cite existing tests). The pytest summary line wins.

Also `README.md` and the card `_examples/42-appendix-b-pytest.md`: `order: 42`, eyebrow "Appendices · pytest reference", a concept title with no count; the card says the configuration and command-line rows run inner pytest sessions with `pytester`.

Deletion table (W1b; each in a fresh scratch copy):

| Check or pinned behaviour | Changed as | Failing test | Why it sees the change |
| --- | --- | --- | --- |
| inner `--import-mode=importlib` | dropped (prepend) | 28 | the collision returns |
| inner `--strict-markers` | dropped | 21 | the marker passes with a warning |
| inner `xfail_strict` / `strict_xfail` | `false` | 22 | `xpassed=1` |
| inner `filterwarnings = ["error"]` | dropped | 24 | `passed=1, warnings=1` |
| teardown order assertion data | outer fixture function-scoped | 1, 2 | extra setup and teardown lines |
| `autouse=True` | removed | 4 | the record is empty |
| `indirect=True` | removed | 6 | the zone string reaches the test, not a `Consignment` |
| `rate_batch` grouping | raises the first error alone | 19 | not an `ExceptionGroup` |
| `quote` log call | message changed | 14 | `caplog.messages` differs |
| `write_quotes` stream | `out: TextIO = sys.stdout` default | 13 | `capsys` captures nothing (executor check) |
| `@warnings.deprecated` | removed | 20 | no warning |
| `pytest_plugins` | moved from a test module into `tests/conftest.py` | whole-repo collection error (executor records the line; this row is the evidence for decision 11) | non-root conftest |
| inner marker registration for 32 | removed | 32 | strict markers refuse it |

### `examples/43-appendix-c-mocking` (project `mocking-reference`, package `mocking_reference`)

- **`carriers.py`**: `ConsignmentId`; frozen slotted `CarrierQuote(carrier: str, total: Decimal)`; `CarrierTimeoutError`; `CarrierGateway` Protocol (`quote(consignment_id, weight_kg, /) -> CarrierQuote`, `book(consignment_id, /) -> str`); `FastlineGateway` (deterministic: 0.45 a kilogram half up, reference `FASTLINE:<id>`, `CarrierTimeoutError` above an illustrative weight); `async def confirm(reference, /) -> str`.
- **`booking.py`**: `type Notify = Callable[[str], None]`; `book_cheapest(gateways: Mapping[str, CarrierGateway], consignment_id, weight_kg, /, *, notify: Notify) -> str` (asks in sorted code order, skips `CarrierTimeoutError`, books the cheapest by `(total, carrier)`, calls `notify(reference)`, `LookupError` when every carrier timed out).
- `py.typed`, and an `__init__.py` that imports nothing.

`tests/conftest.py`: fixture `fastline` (a real `FastlineGateway`); no mocks in conftest.

`test_doubles.py`:
1. `test_spec_set_refuses_setting_a_name_the_spec_lacks`.
2. `test_seal_stops_new_attributes_on_a_configured_mock`.
3. `test_an_assertion_typo_raises_instead_of_passing`.
6. `test_wraps_passes_calls_through_to_the_real_gateway`.
20. `test_async_mock_return_value_is_awaited`.

`test_calls.py`:
4. `test_side_effect_iterable_returns_each_value_then_raises_stop_iteration`.
5. `test_side_effect_callable_computes_the_return_value`.
7. `test_mock_calls_records_calls_in_order_with_call_objects` (`book_cheapest` over two autospecs: `quote` for each code in sorted order, then `book` on the winner).
8. `test_call_args_list_and_any_match_arguments`.
9. `test_assert_has_calls_checks_an_ordered_subsequence`.
10. `test_reset_mock_clears_calls_but_keeps_return_value` x (`default`, `return_value=True`) = 2.

`test_patching.py`:
11. `test_patch_object_replaces_an_attribute_for_the_test` (`autospec=True`: a call without `self`'s arguments is refused).
12. `test_patch_dict_restores_the_mapping_after_the_test` (two cases through `os.environ`: a key added inside, absent after `mocker.stopall()`).
13. `test_mocker_stop_undoes_one_patch`.
14. `test_mocker_patch_used_as_a_context_manager_fails_under_the_warning_filter` (`pytest.raises(PytestMockWarning, match="do not need to be used as context managers")`).

`test_spies.py`:
15. `test_spy_keeps_the_real_behaviour_and_records_returns`.
16. `test_spy_records_the_exception_it_let_through`.
17. `test_stub_records_a_callback` (`book_cheapest(..., notify=mocker.stub(name="notify"))`).
18. `test_resetall_resets_patches_spies_and_autospecs_but_not_stubs`.
19. `test_autospec_of_an_async_function_records_the_await`.

`test_static.py`:
22. `test_mypy_types_mocker_objects_as_mocks` x (`patch`, `patch.object`, `spy`, `stub`, `Mock`) = 5: exact `reveal_type` strings of evidence P. Credits pytest-mock's annotations. Mutation: none in `src` can change them; the witness that the test can fail is a snippet change to `mocker.patch.dict(...)` (executor quotes its revealed type) recorded at W1c.
23. `test_mypy_accepts_a_stub_where_a_callback_is_expected`: `notify=mocker.stub()` gives `[]`; a hand-written `def notify(reference: int) -> None` gives `["arg-type"]`, substring `Notify` or `Callable[[str], None]` (executor check). Credits the `Notify` annotation. Mutation: `notify: object` in `book_cheapest` makes `src` report `[operator]` (executor quotes).

Planned: 22 test functions and 27 cases (`test_doubles.py` 5/5, `test_calls.py` 6/7, `test_patching.py` 4/4, `test_spies.py` 5/5, `test_static.py` 2/6). Number 21 is unused. The pytest summary line wins.

Also `README.md` and the card `_examples/43-appendix-c-mocking.md`: `order: 43`, eyebrow "Appendices · Mocking reference", a concept title with no count; README and card say mocks appear only in the tests and only because the mock API is the subject.

Deletion table (W1c):

| Check or pinned behaviour | Changed as | Failing test | Why it sees the change |
| --- | --- | --- | --- |
| `spec_set=` in test 1 | `spec=` | 1 | setting is allowed |
| `seal` call | removed | 2 | a new attribute appears |
| `wraps=` | removed | 6 | the call returns a `Mock`, not the price |
| `book_cheapest` asks in sorted order | reversed | 7 | `mock_calls` order differs |
| `notify(reference)` | removed | 17 | the stub has no call |
| `FastlineGateway.quote` rate | changed | 15 | `spy_return` differs |
| `FastlineGateway` timeout | removed | 16 | `spy_exception` is `None` |
| `confirm` | made synchronous | 19 | no coroutine; mypy also reports (executor records) |
| `autospec=True` in 11 | removed | 11 | the wrong call is accepted |
| root `filterwarnings = ["error"]` | `-o filterwarnings=default` on the run | 14 | DID NOT RAISE |
| `mocker.resetall()` in 18 | `mocker.stopall()` | 18 | executor check: which assertion fails |
| `(total, carrier)` key | `total` only | executor adds a tie case to 7 or a separate test if nothing fails | |

Rows marked "executor check" are resolved at W1b and W1c or moved to Corrections.

## Steps and status

Step ids are `W*` (decision 0). Only `W1b`, `W1c`, `W4a`, `W4b` and `W4c` are cited as `run:` tokens.

| Step | What | Depends | Status |
| --- | --- | --- | --- |
| W0 | Bookkeeping with dated notes; re-check the pins; record the decisions. `iteration-plan.md`: PDP-141 to 143 `active`, r20 active, r19 closed, PDP-139a to 140c `done`. r19's plan: V6 and V7 closed. Reconciliation plan: rows 249 to 278 `open` with a dated note. `chapters.toml`: 42 and 43 `has_example = true`. Domain rows A to C name the members. Root `pyproject.toml`: `".venv-ft"` in `[tool.ruff] extend-exclude` (decision 7); `verify.sh` green after it. The three stub `description` lines | - | done (2026-11-07) |
| W1a | `_plans/evidence/r20-toolchain-runs.md`: every row of witness table A run in fresh scratch copies (one without a root sync), scrubbed, deleted after use | W0 | done |
| W1b | B member, card and README; one `uv lock`; three green runs and one reverse-order run, from the root and from the member; a whole-repo `--co` run (decision 11); the deletion table and the static mutation, each in a fresh scratch copy (no `.venv`, `uv sync --locked --all-packages`, confirm `pytest_reference.__file__`), deleted after use | W1a | done (2026-11-07) |
| W1c | C member, card and README; one `uv lock` after W1b; three green runs plus one reverse-order run; the deletion table and the static mutations, as W1b | W1b | done (2026-11-07) |
| W2 | Witness results into rows 249 to 278. `_plans/evidence/r20-mock-census.md` (dated greps and per-file API lists, evidence Q). The dated r20 note in `_plans/spikes.md`. Every message, count or value that differs from Planning evidence goes in "Corrections after the build". A failed witness changes the appendix text before prose | W1c | todo |
| W3 | `chapters.toml`: 41 to 43 `status = "drafted"` (kinds unchanged); no figure, `_data/diagrams.yml` unchanged at 41 entries | W2 | todo |
| W4a | A prose agent, plus ch00's one sentence (decision 6): re-fetch every source and quote exactly; re-run any command whose output is quoted, in a fresh scratch copy, and match the run file; hand back witness table A filled with the observed witness per row and a per-paragraph claims table (test, run or source per sentence) | W3 | todo |
| W4b | B prose agent, in parallel with W4a, with the same duties for witness table B | W3 | todo |
| W4c | C prose agent, in parallel, with the same duties for witness table C, plus a check that every census row matches `r20-mock-census.md` | W3 | todo |
| W5 | Opus validation, with up to two repair rounds. After every cut: a seam scan and a dependent-sentence re-read. Also: every witness-table row checked against its witness (a sample of at least one in three re-run or re-fetched by the validator, all quoted output re-run), the excerpt check, the overlap check (criterion 11), the cross-language, outcome and stale-version greps | W4a, W4b, W4c | todo |
| W6 | PR, `ci-ok` green, ask the owner before merge; squash-merge; tag `r20.x` on main; notes-only release | W5 | todo |

Reconciliation rows (step W0). The "How to verify" column uses resolvable tokens.

| # | Ch | Claim | How to verify |
| --- | --- | --- | --- |
| 249 | 41 | From the root, `uv sync --locked --all-packages` installs the dev tools and every member into one environment; without `--all-packages` the exact sync keeps the dev tools, removes every member, and the tests can't import their packages | `run: _plans/evidence/r20-toolchain-runs.md`, `source: https://docs.astral.sh/uv/concepts/projects/sync/` |
| 250 | 41 | Before the root sync, `uv run` in a member builds an environment holding that member alone, with no pytest; after it, `uv run` from a member uses the root environment and removes nothing | `run: _plans/evidence/r20-toolchain-runs.md`, `source: https://docs.astral.sh/uv/concepts/projects/sync/` |
| 251 | 41 | `--locked` and `uv lock --check` refuse a lockfile that no longer matches the pins, with the quoted message | `run: _plans/evidence/r20-toolchain-runs.md` |
| 252 | 41 | `uv init --lib` with `--vcs none --no-readme --no-description --author-from none --name` creates `pyproject.toml`, `src/<package>/__init__.py` and `py.typed` with the `uv_build` backend and leaves the root unchanged; without the flags it also writes a README, a description and the git identity | `run: _plans/evidence/r20-toolchain-runs.md` |
| 253 | 41 | `UV_PROJECT_ENVIRONMENT=.venv-ft uv sync --python 3.15.2t --locked --all-packages` builds a second environment from the same lockfile, in which the GIL is disabled | `run: _plans/evidence/r20-toolchain-runs.md`, `source: https://docs.astral.sh/uv/concepts/projects/config/` |
| 254 | 41 | mypy, ruff and pytest each take settings from the first configuration file they find and never merge two, so a tool table in a member replaces the root's for that member | `run: _plans/evidence/r20-toolchain-runs.md`, `source: https://mypy.readthedocs.io/en/stable/config_file.html`, `source: https://docs.astral.sh/ruff/configuration/` |
| 255 | 41 | mypy 2.4.1's `--strict` enables the listed flags, `--warn-redundant-casts` among them, and not `--warn-unreachable`, which the root config adds | `run: _plans/evidence/r20-toolchain-runs.md`, `source: https://mypy.readthedocs.io/en/stable/command_line.html` |
| 256 | 41 | mypy over two members' tests from the root stops with a duplicate-module error; the per-member runs pass | `run: _plans/evidence/r20-toolchain-runs.md` |
| 257 | 41 | The root `select` replaces ruff 0.17.4's default rule set, enabling the stated number of rules from the ten named linters against the default's stated number | `run: _plans/evidence/r20-toolchain-runs.md`, `source: https://docs.astral.sh/ruff/settings/` |
| 258 | 41 | Outside a git checkout ruff lints `.venv-ft` unless the root `extend-exclude` names it; with the line, `ruff check .` and `ruff format --check .` pass | `run: _plans/evidence/r20-toolchain-runs.md` |
| 259 | 41 | The `deprecated` error code is off under `--strict` and reports a deprecated call once enabled | `run: _plans/evidence/r20-toolchain-runs.md` |
| 260 | 42 | Under the root configuration an unregistered marker stops collection, a configuration warning is an error, a passing `xfail` fails the run under either option name, and a warning fails its test; pytest 9's `strict` enables the four strictness options | `test_an_unregistered_marker_fails_collection_under_strict_markers`, `test_an_unknown_option_fails_under_strict_config`, `test_a_passing_xfail_fails_the_run_under_strict_xfail`, `test_filterwarnings_error_turns_a_warning_into_a_failure`, `test_strict_enables_the_four_strictness_options`, `source: https://docs.pytest.org/en/stable/reference/reference.html` |
| 261 | 42 | The first configuration file pytest finds wins, and two are never merged | `test_the_first_config_file_wins_and_is_not_merged`, `source: https://docs.pytest.org/en/stable/reference/customize.html` |
| 262 | 42 | Two test files with one basename collide under the prepend mode and both run under importlib, where a test module can't import `conftest` by name | `test_same_basename_test_files_collide_under_prepend`, `test_importlib_mode_gives_each_test_file_a_unique_name`, `test_importlib_mode_cannot_import_conftest_by_name`, `source: https://docs.pytest.org/en/stable/explanation/pythonpath.html` |
| 263 | 42 | `pytest_plugins` in a non-root conftest fails collection; in a test module it loads the plugin from the root and from the member | `test_pytest_plugins_in_a_non_root_conftest_fails_collection`, `run: W1b`, `source: https://docs.pytest.org/en/stable/how-to/plugins.html` |
| 264 | 42 | Yield fixtures tear down in reverse order of setup, a module-scoped fixture is set up once, and the factory, autouse, usefixtures, indirect and getfixturevalue forms behave as listed | `test_yield_fixtures_tear_down_in_reverse_order_of_setup`, `test_a_module_scoped_fixture_is_set_up_once_for_the_module`, `test_a_factory_fixture_builds_a_fresh_object_per_call`, `test_an_autouse_fixture_runs_without_being_named`, `test_usefixtures_applies_a_fixture_whose_value_is_unused`, `test_an_indirect_parameter_reaches_the_fixture_as_request_param`, `test_getfixturevalue_resolves_a_fixture_by_name` |
| 265 | 42 | `pytest.param` names a case and can carry a mark, stacked parametrize decorators multiply, and duplicate ids get a suffix unless `strict_parametrization_ids` is set | `test_pytest_param_ids_name_the_cases`, `test_a_case_can_carry_its_own_mark`, `test_stacked_parametrize_takes_the_cross_product`, `test_duplicate_ids_get_a_suffix_unless_strict_parametrization_ids` |
| 266 | 42 | `tmp_path`, `capsys` and `caplog` give a fresh directory, the captured output and the captured records; mypy checks a typed fixture's use; the `monkeypatch` rows are the existing tests | `test_tmp_path_is_a_fresh_directory_per_test`, `test_capsys_captures_what_the_report_writes`, `test_caplog_records_the_quote_message`, `test_mypy_checks_a_typed_fixture_use`, `test_validity_reads_the_environment_and_the_context_restores_it`, `test_monkeypatch_refuses_a_misspelt_name` |
| 267 | 42 | `raises` matches with `re.search` and can check the exception object, `RaisesGroup` and `RaisesExc` match an exception group's members, and `warns` matches a deprecation | `test_raises_match_is_a_regex_search`, `test_raises_check_tests_the_exception_object`, `test_raises_group_matches_the_batch_failures`, `test_warns_matches_the_deprecation`, `source: https://docs.pytest.org/en/stable/reference/reference.html` |
| 268 | 42 | `-k`, `-m`, `-x`, `--lf`, `--co` and `-o` select, stop, rerun, list and override as stated | `test_k_selects_by_name_expression`, `test_m_selects_by_marker`, `test_x_stops_at_the_first_failure`, `test_lf_reruns_only_the_last_failures`, `test_collect_only_lists_without_running`, `test_o_overrides_an_ini_option` |
| 269 | 43 | The book mocks in three chapters' tests and nowhere in `src`, in the stated order of preference | `run: _plans/evidence/r20-mock-census.md`, `test_book_best_books_only_the_winner`, `test_patching_the_name_where_it_is_looked_up_replaces_the_carrier` |
| 270 | 43 | `spec_set` refuses setting an unknown name, `seal` stops new attributes, an assertion typo raises, and `wraps` passes calls through | `test_spec_set_refuses_setting_a_name_the_spec_lacks`, `test_seal_stops_new_attributes_on_a_configured_mock`, `test_an_assertion_typo_raises_instead_of_passing`, `test_wraps_passes_calls_through_to_the_real_gateway`, `source: https://docs.python.org/3/library/unittest.mock.html` |
| 271 | 43 | An iterable `side_effect` returns each value then raises `StopIteration`, a callable one computes the result, and `mock_calls`, `call_args_list`, `ANY`, `assert_has_calls` and `reset_mock` record and check calls as stated | `test_side_effect_iterable_returns_each_value_then_raises_stop_iteration`, `test_side_effect_callable_computes_the_return_value`, `test_mock_calls_records_calls_in_order_with_call_objects`, `test_call_args_list_and_any_match_arguments`, `test_assert_has_calls_checks_an_ordered_subsequence`, `test_reset_mock_clears_calls_but_keeps_return_value` |
| 272 | 43 | `mocker.patch.object` with `autospec` checks calls, `mocker.patch.dict` restores the mapping, `mocker.stop` undoes one patch, and `mocker` patches used as context managers warn, which fails under the root filter | `test_patch_object_replaces_an_attribute_for_the_test`, `test_patch_dict_restores_the_mapping_after_the_test`, `test_mocker_stop_undoes_one_patch`, `test_mocker_patch_used_as_a_context_manager_fails_under_the_warning_filter`, `source: https://pytest-mock.readthedocs.io/en/stable/usage.html` |
| 273 | 43 | A spy keeps the real behaviour and records returns and exceptions, a stub records a callback, and `resetall` resets patches, spies and autospecs but not stubs | `test_spy_keeps_the_real_behaviour_and_records_returns`, `test_spy_records_the_exception_it_let_through`, `test_stub_records_a_callback`, `test_resetall_resets_patches_spies_and_autospecs_but_not_stubs`, `source: https://pytest-mock.readthedocs.io/en/stable/usage.html` |
| 274 | 43 | An autospec of an async function returns a coroutine on call and records the await; an `AsyncMock`'s return value is awaited | `test_autospec_of_an_async_function_records_the_await`, `test_async_mock_return_value_is_awaited` |
| 275 | 43 | mypy types `mocker` objects as the stated mock types and accepts a stub where a callback is expected, while refusing a callback of the wrong shape | `test_mypy_types_mocker_objects_as_mocks`, `test_mypy_accepts_a_stub_where_a_callback_is_expected`, `source: https://github.com/python/typeshed/blob/main/stdlib/unittest/mock.pyi` |
| 276 | 42-43 | mypy `--strict`, ruff and the idiom scan pass both members, three runs and one reverse-order run with the same count | `run: W1b`, `run: W1c` |
| 277 | 41-43 | Every command, flag and option stated in the three appendices has its witness in the filled witness tables | `run: W4a`, `run: W4b`, `run: W4c` |
| 278 | 0 | `--all-packages` matters because only with it does the root sync install the members | `run: _plans/evidence/r20-toolchain-runs.md` |

No legacy rows are carried.

## Corrections after the build
- Step W1a: `_plans/evidence/r20-toolchain-runs.md` recorded on 2026-11-07, and every witness-table-A row matches the plan except these. The `--isolated` rules fall into 38 letter groups (the plan's 46 counted finer prefixes); the 279 and 407 rule counts match. `ruff check --diff` exits 1 and reports "Would fix 5 errors" against 4 reported. The default build prints `True 0`. The probe's long line is 108 columns, not 110. The `deprecated` message line number depends on the probe file. During W1a one `uv sync --locked --all-packages` ran in the real repo instead of a copy; it printed nothing and changed no tracked file.

The orchestrator records here every handback that differs from this plan: messages, counts, which tests a deletion fails, word counts, declined findings, witness rows added or cut.

- Step W0: done 2026-11-07, no deviation from the row. The pins were not re-fetched from PyPI by the executor (the caller carried the 2026-11-07 check); `uv lock --check` and `verify.sh` pass on the unchanged pins. r19's V6 and V7 are marked done; PDP-139a to 140c are `done` and PDP-141 to 143 `active`. Rows 249 to 278 were added to the reconciliation plan as `open` with a dated note, and the three domain rows A to C name their members (A has none). `chapters.toml` sets `has_example = true` for 42 and 43 (status stays `stub`; W3 changes it). The three stub `description` lines are one-sentence drafts. Decision 7: `".venv-ft"` is in the root `extend-exclude`; in a copy without `.git` and with `.venv-ft` present, `ruff check .` printed `All checks passed!` and `ruff format --check .` `610 files already formatted`. `verify.sh` passed (1312 tests) after the change.

- Step W1b: done 2026-11-07. Final counts from the pytest summary line: 43 passed in the member (the plan's "43 cases" was a miscount: its own breakdown gives 40), 1355 in the whole repo (1312 plus 43), `--co` over the whole repo collects 1355 with no error.
- Step W1b: three tests were added beyond the spec because `src` pinned behaviour no test saw: `test_a_non_positive_weight_is_refused`, `test_a_quote_rounds_half_up_to_the_cent` (3.3 kg at 0.45 is 1.485, so half up gives 1.49 and half even 1.48) and `test_a_clean_batch_returns_its_quotes_in_order`, in `tests/test_rating.py`. Deletions of the weight check, the rounding mode, the ASIA rate, the batch order and `MAX_KILOGRAMS` each fail a test.
- Step W1b: an in-process `pytester` session inherits the outer run's warning filters. Under the root `filterwarnings = ["error"]` the inner `PytestUnknownMarkWarning` of the lenient runs became an error (tests 21 and 26 failed; evidence K saw the leak only for `DeprecationWarning`, which pytest re-enables itself). `tests/test_config.py` therefore has an autouse fixture `fresh_warning_filters` (`warnings.catch_warnings()` plus `resetwarnings()`); without `autouse` tests 21 and 26 fail. The other modules need no such fixture. B should say so. `runpytest_subprocess` was not needed.
- Step W1b: observed values that differ from, or settle, the plan. Stacked parametrize ids come out `[1-EU]`, `[1-ASIA]`, `[5-EU]`, ... (the decorator nearest the function varies slowest and is named first), not `[EU-1]`. `raises(match=)` with an unmatched anchor raises `AssertionError` whose message starts `Regex pattern did not match`; a false `check=` raises `AssertionError` ending `did not return True`; both are matched by nested `pytest.raises(AssertionError, match=...)` (test 17, 18). `--strict-config` and `strict = true` with an unknown option give exit code `USAGE_ERROR` and `Unknown config option: unknown_option` on stderr, and without them one warning (`passed=1, warnings=1`). Test 30 runs `runpytest()` from the inner root (running `runpytest("sub")` treats `sub/conftest.py` as top level and passes); the message is `Defining 'pytest_plugins' in a non-top-level conftest is no longer supported`. Test 34 `--lf` prints `run-last-failure: rerun previous 1 failure` and the summary is `1 failed`. The mypy snippet of test 37 assigns the result (`captured = ... + 1` in a function returning `None`): returning it adds `no-any-return`, so the codes were `["no-any-return", "operator"]`.
- Step W1b: test 32 (`-m`) first passed under `-m "not bulk"` because the outcome counts are the same (`passed=1, deselected=1`); it now also lists the selected node id.
- Step W1b: `uv lock` once (`Added pytest-reference v0.1.0`; the only `uv.lock` change is six lines). `verify.sh` was first started three times in one loop, which the tool moved to the background and the executor stopped when a new test file was added; the final three runs, after the last edit, each ended `verify: all steps passed` with 1355 tests. Reverse order is the nine test files in reverse alphabetical order, from the member directory and from the root: 43 passed in each, as in the three forward runs from each. Voice scan `--tier ban --fail --exclude .venv-ft`: 0; idiom scan: 0; `host_ids.py check`: 0.
- Step W1b: deletion table, each in a fresh scratch copy (no `.venv`, `uv sync --locked --all-packages`, `pytest_reference.__file__` confirmed inside the copy), copies deleted. Failing test per change: importlib dropped, 28; `--strict-markers` dropped, 21; `xfail_strict`/`strict_xfail` false, 22 (both cases); `filterwarnings` dropped, 24; outer fixture function-scoped, 1 (and, for the module fixture of 2, 2: each alone); `autouse=True` removed, 4 and 5 (5 also needs the autouse entry in its expected list); `indirect` removed, 6 (both cases); `rate_batch` raises the first error, 19; log message changed, 14; `out: TextIO = sys.stdout` default, 13; `@warnings.deprecated` removed, 20 and 24; marker registration removed, 32 (the plan's "refuses" reason holds: `'bulk' not found in `markers` configuration option`). The `pytest_plugins` row: moving the line from the six test modules into `tests/conftest.py` leaves the member at 43 passed but the whole-repo collection reports `ERROR examples/42-appendix-b-pytest/tests - Failed: Defining 'pytest_plugins'...` and `1312 tests collected, 1 error`.
- Step W1b: further mutations, each failing the named test only unless stated: `usefixtures` mark removed, 5; `fresh_warning_filters` not autouse, 21 and 26; static annotation `capsys: object`, 37 (`attr-defined` replaces `operator`); anchor removed from the nested `match`, 17 (`DID NOT RAISE`); `check` made true, 18; `-x` dropped, 33; `--lf` dropped, 34; `-k asia` widened, 31; `-m bulk` inverted, 32; `--collect-only` dropped, 35 (the file `ran.txt` exists); `-o` value inverted, 36; `--strict-config` dropped, 23; `strict = true` dropped, 25 (all four cases); inner subdirectory config removed, 26; prepend replaced by importlib, 27; conftest-import run under prepend, 29; inner `sub/conftest.py` emptied, 30; per-case `marks` emptied, 9; id renamed, 8; second parametrize narrowed, 10; `strict_parametrization_ids` false, 11; a module-scoped `tmp_path` override in the inner test, 12; `functools.cache` on the factory, 3; `getfixturevalue` of another name, 7; `MAX_KILOGRAMS` 2000, 18 and 19; half-even rounding, the half-up test; `Weight` check disabled, the weight test; ASIA rate 1.30, one indirect case and the clean-batch test; `quotes[::-1]`, the clean-batch test.
- Step W1b: reader text. The card description says most of the rows run through an inner session (23 of 35 test functions use `pytester`). The README states the warning-filter fixture. Nothing in the member names a path; `pytester` output was never quoted. W0's reconciliation rows 249 to 278 still make `validate.py` report 30 `unresolved evidence` errors; they close at W2.

- Step W1c: done 2026-11-07. Final counts from the pytest summary line: 32 passed in the member (26 test functions: `test_doubles.py` 6, `test_calls.py` 6, `test_booking.py` 3, `test_patching.py` 4, `test_spies.py` 5, `test_static.py` 2; the plan's 27 cases and 22 functions were a miscount, its own breakdown gives 29 cases), 1387 in the whole repo (1355 plus 32), `--co` over the whole repo collects 1387 with no error. `uv lock` once (`Added mocking-reference v0.1.0`). Three forward runs from the member and three from the root, plus a reverse-order run (the five test files in reverse alphabetical order) from each: 32 passed every time; `verify.sh` ended `verify: all steps passed`. Voice scan 0, idiom scan 0, `host_ids.py check` 0.
- Step W1c: tests added beyond the spec because `src` or the API pinned behaviour no planned test saw: `tests/test_booking.py` (`test_a_tie_on_total_goes_to_the_carrier_name_that_sorts_first`, `test_a_carrier_that_times_out_is_skipped`, `test_every_carrier_timing_out_raises_lookup_error`) and `test_a_magic_mock_supports_the_magic_methods_a_mock_lacks` in `test_doubles.py` (witness for the `MagicMock` row). The tie test is the plan's `(total, carrier)` row: replacing the key with the total alone fails it.
- Step W1c: observed values that differ from, or settle, the plan. Test 9 is named `test_assert_has_calls_checks_a_contiguous_ordered_run`, not "ordered subsequence": `assert_has_calls([call("CN-1"), call("CN-3")])` over calls 1, 2, 3 raises `AssertionError` matching `Calls not found`, and `any_order=True` accepts it. `Mock(unsafe=True)` is not inherited by child mocks: `unchecked.book.assret_called_once()` still raised, so test 3 calls `assret_called_once` on the `unsafe=True` mock itself. A `spec`ed mock allows `loose.cancel = "set"`, a `spec_set` one raises `Mock object has no attribute 'cancel'` on set and on get. `mocker.patch.object(FastlineGateway, "quote", autospec=True, ...)` records `self`: `assert_called_once_with(gateway, CN1, TEN)`; a call with no arguments raises `TypeError` matching `missing a required argument`, and mypy reports `call-arg` for it, so that line carries one named `# type: ignore[call-arg]`. Test 7 attaches both autospecs to one `mocker.Mock()` manager with `attach_mock`, so the cross-gateway order is `[call.airco.quote(...), call.fastline.quote(...), call.fastline.book(...)]`. The `reveal_type` strings of evidence P hold exactly (union of `MagicMock | AsyncMock | NonCallableMagicMock` for `patch` and `patch.object`, `pytest_mock.plugin.SpyType`, `unittest.mock.MagicMock`, `Any`), and the exit status of a run that only reveals is 0, not 1. `mocker.patch.dict(...)` also reveals `Any` (the quoted witness for test 22). A wrong callback taking an `int` gives exactly `["arg-type"]`.
- Step W1c: deletion table, each in a fresh scratch copy (no `.venv`, `uv sync --locked --all-packages`, `mocking_reference.__file__` confirmed inside the copy), copies deleted. Failing test per change: `spec_set=` to `spec=`, 1; `seal` removed, 2; `wraps=` removed, 6; `sorted(gateways)` reversed, 7; `notify(reference)` removed, 17 (`test_stub_records_a_callback`); rate 0.45 to 0.50, 15, and also 6 and 11; timeout limit raised, 16; `confirm` made synchronous, 19 (`TypeError: An asyncio.Future, a coroutine or an awaitable is required`), and mypy `--strict src tests` still prints `Success`, so the plan's "mypy also reports" does not hold; `autospec=True` removed, 11; `-o filterwarnings=default`, 14 (the run ends `1 failed, 31 passed, 1 warning`); `mocker.resetall()` to `mocker.stopall()`, 18; key `(total, carrier)` to total only, the tie test. Further mutations: `mocker.stop` removed, 13; `stopall` removed in 11, 11; `stopall` removed in 12, both cases; `unsafe=True` removed, 3; `any_order=True` removed, 9; `reset_mock(return_value=...)` to a plain `reset_mock()`, the `return_value=True` case of 10 only; `continue` to `raise`, the skip test and the all-timed-out test; the `if not offers` check disabled, the all-timed-out test; `MagicMock` to `Mock`, the magic-method test; an expected `call` changed, 8; `side_effect` callable removed, 5; an extra iterable item, 4; `AsyncMock` to `Mock`, 20.
- Step W1c: static mutations. `notify: Notify` to `notify: object` in `booking.py` fails test 23 with `assert [[], []] == [[], ['arg-type']]`: mypy accepts the wrong callback and reports no `[operator]` from `src` (errors in the imported package are not reported through the snippet run), so the plan's "reports `[operator]`" is wrong. Using `mocker.stub()` in place of the wrong callback fails test 23 the same way. Changing the expected `Mock` string to `unittest.mock.MagicMock` fails test 22 (`assert ['Any'] == ['unittest.mock.MagicMock']`); the same expectation with a `mocker.patch.dict({}, a=1)` snippet also reveals `Any`.
- Step W1c: reader text. The README and card say mocks appear only in the tests. Nothing in the member names a path.

Lessons carried from r11-r19, which this plan applies up front:
- **Counts.** Per-file counts are summed from the spec, and the pytest summary line wins (r13 to r19; the builds of r16 to r19 all added tests the deletion runs needed).
- **Members.** Named after the package, with no `[tool.*]` table (r13); created with `uv init` and `--author-from none` (evidence F).
- **importlib conftest rule.** A test module can't import `conftest` or another test module; shared values go through fixtures, conftest types under `TYPE_CHECKING` (r13, r14, r19 J). B turns it into rows 262 and 263.
- **Determinism.** Lists or tuples only in failing assertions, never a set or dict repr (r13 to r17); no path in an assertion (pytester's base directory names the account).
- **Witness strength.** An assertion of `!= []` or `pytest.raises` on an exception the harness can also raise is no witness (r18 U1b, r19 E): `pytester` outcomes are exact counts, and test 14 matches the warning's text, not just its class. A test whose failure comes last can't witness `-x` (evidence N).
- **Self-referential oracle** (r19 experiment a): an expected value is a literal, never computed by the code under test.
- **Reader commands.** No repo script beyond the ones ch00 already gives (`verify.sh`, `check-prereqs.sh`), and never `host_ids.py` (r15).
- **Pointers.** None that describes a stub's content (Appendix D stays unmentioned), none circular (r14, r16, r19).
- **Claim scrutiny.** Cards, READMEs, conftest and `src` docstrings get the same review as the appendices (r14 to r19).
- **Quotations** stop where the page's sentence stops, and before a dash (r18 U6, evidence L); a heading that trips the ban tier is cited through another heading (r18 U5).
- **Unversioned docs.** Where a page has no version and the pinned binary disagrees, the recorded run wins (evidence A).
- **Voice.** "earns its place" is banned (r15); the voice scan needs `--exclude .venv-ft`.
- **Paths.** Repo-relative only in plans (r09); `<scratchpad>` in place of the scratch path.

## Acceptance criteria

`S=~/.claude/skills/lgtm-professional-voice/scripts/scan.sh` throughout.

1. `bash scripts/verify.sh` prints `verify: all steps passed`, also with `.venv-ft` present in a copy without `.git` (decision 7). `uv lock --check` passes, and the only `uv.lock` change is the two new members.
2. Each new member passes `uv run pytest` and `uv run mypy --strict src tests` on three consecutive runs and once in reverse file order, with the same pass count, from the member directory and from the root; a whole-repo `uv run pytest --co -q` collects with no error.
   - `grep -rnE "time\.|perf_counter|datetime|random|sleep|socket|urllib|requests|httpx"` over both members' `tests` prints nothing.
   - `grep -rnE "monkeypatch|mocker|unittest\.mock|\bpatch\b|\bAny\b|cast\(|print\(|Optional|random|\bglobal\b|sys\.modules|time\.|datetime|exec\(|eval\(|subprocess|socket|urllib|http"` over both members' `src` prints nothing.
   - `grep -rnE "mocker|unittest\.mock"` over B's `tests` prints nothing; `pytest_plugins` appears in B's test modules only, never in a conftest.
3. Every test name cited in rows 260-275 is defined exactly once across `examples/*/tests`.
4. Static tests assert their exit status, an exact sorted code list or exact `reveal_type` strings, and no line number. Every `# type: ignore[...]` and `# noqa` names a code, and there are no unused ignores.
5. Every static test fails on its named mutation (W1b, W1c quote the line).
6. Deletion tables: every row, changed in a fresh scratch copy, makes the named test fail for the stated reason; the handback quotes the failing line. Executor-check rows are resolved or moved to Corrections.
7. Every "refuses", "fails", "stops", "removes", "restores", "records", "resets", "warns" or "wins" sentence names a test, a run-file line or a source sentence; `pytester` tests assert exact outcome counts. Scope words name the test that covers the whole scope, or are cut.
8. Appendices 41-43 are drafted, with no figure include, the appendix spine, no `## Reference` heading, and at most 2,500 prose words each by `validate.py` (a warning below 1,900 is reported, not padded).
9. No sidebar: `grep -c '<blockquote class="ai-sidebar"'` is 0 in 41-43, and `{: .ai-sidebar}` appears nowhere.
10. Thesis:
    - A states the no-merge rule for each tool with its source, the exact-sync trap, and the free-threaded commands.
    - B gives each root configuration line its test and states the importlib consequence for `conftest.py`.
    - C states the order of preference before any API row, matches the census, and says once that a mock bypasses the static check.
11. Pointers, promises and overlap (evidence S):
    - B lists the rest of fixtures, parametrization and configuration (promise 1); C lists the rest of the mock API (promise 2) and collects the patch API with a pointer to B's `monkeypatch` rows (promise 3).
    - Pointers use exact front-matter titles; none describes Appendix D.
    - A doesn't repeat ch00's install, clone, check-prereqs, gate-order, troubleshooting or pin-bump walkthroughs; B and C don't repeat ch11's method, four-doubles table or experiments; C doesn't re-teach ch33's lookup rule beyond one quoted sentence and its tests.
    - ch00 differs from main by the one rewritten `--all-packages` sentence only.
12. Voice:
    - `$S --tier ban --fail --exclude .venv-ft` exits 0 over the three appendices, ch00, both READMEs and cards, with `--stats` reviewed. "earns its place" appears nowhere.
    - Uncontracted `does not|do not|is not|are not|did not|cannot` appear at most 3 times per appendix outside code, output and quotations.
    - British spelling: `grep -nE "\b(behavior|favor|color|organiz|recogniz|analyz|initializ|customiz|serializ|finaliz|optimiz|synchroniz|parallelizat|utiliz)"` over prose (quotations, code, flags and API names excluded) prints nothing.
13. No em or en dash in any file touched in r20, including this plan: `grep -cP "\x{2014}|\x{2013}"` is 0. Quotations stop before any dash on the source page.
14. `grep -nE "Java|JavaScript|C#|C\+\+|\.NET|\bGo\b|Rust|capstone|PDP-|\br[0-9]{2}\b|spike|[Cc]hapter [0-9]"` over `_docs/41-*.md`, `_docs/42-*.md`, `_docs/43-*.md`, the new READMEs and the cards prints nothing.
15. Idiom scan (`lgtm-idiomatic-review`): 0 ban-tier in both members' `src` and `tests`.
16. `python3 scripts/host_ids.py check` exits 0. Quoted output shows `<repo>` and comes only from fresh runs scrubbed before quoting; no pytester base-directory path appears in any tracked file.
17. Every excerpt matches its source byte for byte (the root `pyproject.toml` excerpts match the file after W0). Indented multi-method excerpts are wrapped in `<!-- fmt:off -->`/`<!-- fmt:on -->`. Excerpts containing `{{` are wrapped in `{% raw %}`.
18. Every witness table row is filled by its prose agent with the observed witness; the validator re-runs or re-fetches at least one row in three, and every quoted command output.
19. Attribution: every docs quotation is exact, attributed and stops where the page's sentence stops; Okken and Meszaros by title only; every book cited is already in `bibliography.html`. Nothing is copied beyond the quoted sentences.
20. Claims:
    - Every factual sentence maps to a named test, a `run:` token, the census or run file, or a fetched source URL linked in the appendix, in the prose agent's claims table.
    - No outcome statistic: `grep -niE "percent|%|most (teams|projects|developers)|productiv|in production"` over the three appendices prints nothing outside code.
    - `validate.py`, `--self-test` and `--claims` exit 0 with rows 249-278 resolved; `check_stale_versions` reports nothing for the three appendices.
21. `scripts/site-build.sh` succeeds and `git status` is clean afterwards (`Gemfile.lock` unchanged). `_data/diagrams.yml` has 41 entries, unchanged.
22. Reconciliation rows 249-278 are `verified` or `adjusted` with evidence.
23. Deterministic: no test depends on wall time, absolute paths, hash order, test order or the network. `filterwarnings = ["error"]` stays in the root config.
24. CI `ci-ok` is green on the PR; `ci.yml` is unchanged (decision 12). Merge happens only after the owner's explicit approval.
25. Test counts in prose and handbacks come from a fresh pytest summary line.
26. Repo-relative paths only: a grep for home-directory roots and the pytester base-directory prefix over the files touched in r20 (this plan excluded, since it names the patterns) prints nothing, and `host_ids.py check` exits 0.

## Risks

- **Docs drift from the pins.** uv's and ruff's pages aren't versioned and can describe a newer release. The run file is the version witness; a page sentence is quoted only where it agrees with the run. A later pin bump must re-run W1a's rows before release; A says which versions it describes.
- **Stale-version check.** uv's free-threading sentence and similar pages name an older minor ("Python 3.14+"); `check_stale_versions` flags it in reader text unless preceded by "since", "before", "until" or "new in". A doesn't quote it (evidence J); W4a greps before handback.
- **Liquid.** `ci.yml` lines with `${{ ... }}` and any f-string with `{{` must be inside `{% raw %}`; the planned ci excerpt avoids them.
- **pytester in-process runs.** Inner sessions import test modules into the outer interpreter; if one leaks state or a warning into the outer session, W1b switches that test to `runpytest_subprocess` and records why. Inner output names the account through the base temporary directory: never asserted, always filtered before quoting.
- **Predicted messages and counts.** Expect differences in exact outcome dictionaries (for example `deselected` counts under `--lf`, evidence N), in ruff rule counts, in mypy's code for a wrong callback (`[arg-type]` against `[misc]`) and in `reveal_type` strings. Tests match exact values observed at W1b and W1c, and Corrections records each difference.
- **Word budgets.** Tables don't count, so each appendix may fall below the 1,900 floor; that's a warning, reported. If one exceeds 2,500, cut prose that restates a table row first, then the pointer sentences.
- **Overlap.** The likeliest defect is re-teaching ch00's walkthrough in A or ch11's doubles in C; criterion 11 and W5 check it.
- **Config changes.** Decision 7 touches the root `pyproject.toml`; W0 runs `verify.sh` before any other step. Decisions 8 to 10 leave config alone; if the owner reverses one, its ch11 or ch00 dependencies move into this iteration and the criteria gain a row.
- **`uv init` identity.** Run without `--author-from none`, it writes the git identity into a tracked file; criterion 16 and the member steps guard it.
- **`uv.lock` races.** W1b and W1c are sequenced.
- **Nothing upstream.** No finding in r20 goes to a project without the owner, through `lgtm-issue-reporting`.
