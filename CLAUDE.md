# CLAUDE.md: Design Patterns with Python

Ground rules for working in this repo. Read `_plans/r01-build-plan.md` (and the plan for the
current iteration) for scope, status board and acceptance criteria before starting work. Plans
are the source of truth and are never edited by content executors. This file is internal and may
use chapter numbers and PDP codes; reader-facing files may not.

This is the fourth book in the series. The C++, Java and C# books are reference-only for process
and series conventions. They are not a code source: never port their examples. Every example is
written fresh in the shipping domain.

## Thesis

The book sorts the GoF patterns three ways, and every pattern chapter says which bucket it is in:

- **Dissolved**: Python's language features make the pattern a few lines or nothing (Strategy is a
  callable, Iterator is a generator, Singleton is a module).
- **Survives**: the pattern is still real design (State machines, Command with undo, Composite).
- **Needs disambiguating**: the name is shared with something else in Python. The headline case is
  the **Decorator pattern** (GoF wrapper objects that compose behaviour at runtime, stacks as data)
  versus the **`@decorator` syntax** (a function rebinding at definition time). Keep the two names
  apart in prose and code, and never let a chapter blur them.

The thesis is temporal: modern Python 3.15 against the 1994 assumptions a pattern was written
under. It is not one language against another. There is no cross-language comparison anywhere in
reader-facing text.

## Toolchain

- **Fedora 44, local tools only. No containers in the book**: no Docker, Kubernetes, UI or web
  front end in any example or chapter.
- **uv workspace.** One root `pyproject.toml` (virtual root, `package = false`, members
  `examples/*` and `spikes/*`), one `uv.lock`, exact `==` pins in the root `dev` group (pytest,
  pytest-mock, ruff, mypy), `.python-version` exact 3.15.x. Members carry no `[tool.*]` tables,
  because a member table would shadow the root's.
- One-time setup: `uv sync --locked --all-packages`. Inside a member directory `uv run` treats the
  member as the project and does not see the root dev group; the shared root `.venv` fixes that.
- **mypy runs per member** (`cd <member> && uv run mypy --strict src tests`), looped by
  `scripts/verify.sh`, because same-basename test files (`test_model.py`) collide as duplicate
  modules in a single root run. pytest runs once from the root (`--import-mode=importlib`).
- Gates: `scripts/check-prereqs.sh` (toolchain), `scripts/verify.sh` (ruff check, ruff format
  --check, mypy per member, mypy on scripts, pytest), `scripts/validate.py` (book checks, also
  `--self-test`), `scripts/host_ids.py check`.
- **Jekyll is built only through `scripts/site-build.sh`**, in a `ruby:4.0.9` container under
  Docker Engine, because the host lacks `ruby-devel`. Never podman (not installed). The container
  is a build tool only and never appears in reader pages. `Gemfile.lock` must come out unchanged.
- Latest stable versions, pinned exactly, re-verified against upstream before each release
  (the dated table is in the build plan). No pre-release, nothing needing a licence key.
- Language floor: Python 3.15. Use the 3.15 idioms where they fit (PEP 695 generics, `type`
  aliases, `typing.override`, deferred annotations, `frozendict`, `sentinel`); say so when mypy lags a feature.

## Repo layout

```
_docs/NN-slug.md         chapters (47 docs: 0-40 plus appendices A-F as 41-46)
_parts/                  part pages
_examples/               example cards (a collection)
_data/diagrams.yml       figure registry: name, section, title, caption
diagrams/specs/*.py      one spec per figure (source of truth)
diagrams/*.svg|.excalidraw  generated pairs; never hand-edit
examples/NN-slug/        one uv member per chapter example (src/, tests/)
spikes/                  evidence for decisions, not reader code
scripts/                 verify.sh, validate.py, check-prereqs.sh, site-build.sh,
                         host_ids.py, generate_diagram.py, render_diagrams.py, chapters.toml
_plans/                  plans and status; verification status lives only here
.github/workflows/       ci.yml (ci-ok summary job), pages.yml
```

## Chapter spine and depth

Every chapter follows the same shape: learning objectives; why this matters; the figure; the body;
"Build, run, observe" on hands-on chapters; "When not to use it" on every pattern chapter, holding
the one AI sidebar; "For deeper coverage" citing this book's `/bibliography/`, kept in step with the hub's
`books.yml` (the chapter text never says "the hub"). The figure walk-through paragraph stays: it is
the figure's text alternative.

- Body prose targets **1,900-2,500 words**, excluding code and diagrams. The ceiling is an error in validate.py; the floor is a warning (owner decision 2026-11-05): length serves the reader, so never pad to reach it and never cut a fact to sit under the ceiling.
- **One paired SVG + `.excalidraw` figure per chapter**, generated with `lgtm-diagram-generator`
  from a spec in `diagrams/specs/`. Never hand-edit an SVG: change the spec and regenerate.
- **Figures are generated after the green example**, using the real type and function names from
  the code. Vertical flow for pipelines. Emphasis boxes are light fill with dark text.
- **Captions are 20-45 words**, one or two sentences, a gloss and not an identifier inventory; no
  angle-bracket generics. The HTML caption may start `Figure N.1:`, but no numbers appear inside
  SVGs or in body prose (no baked-in chapter or part numbers).
- **AI sidebar**: exactly one per pattern chapter, written as an explicit
  `<blockquote class="ai-sidebar" markdown="1">` ... `</blockquote>`. Never the kramdown form
  `{: .ai-sidebar}` (it breaks blockquote parsing under kramdown-GFM). The check is
  `grep -c '<blockquote class="ai-sidebar"'` equals 1. Content (lgtm-professional-voice, 2026-11-05;
  wording settled in r25): open with what the request leaves open ("'Write the pricing strategies'
  leaves the shape and the rounding open"), then give a ready-to-paste sample prompt as a nested `>`
  quote that bakes in the chapter's decision rule, then at most one line of review action. Never a
  claim about what an assistant does or may write ("an assistant may ..."), because no test in the
  book witnesses it. The bold lead-in names what is being specified ("Specifying X"), not
  "Reviewing assistant-written X".
- **Structure** (lgtm-professional-voice, 2026-11-05): intent before mechanism; explain a subtle
  mechanism by a minimal example first; prose doesn't re-narrate a code block (the code shows how;
  prose adds the force, the trade-off, the domain fact); close by mapping each learning objective
  to what the reader can now do and the artifact that delivered it.
- **No "as we saw in Chapter N"** and no chapter-number cross-references in prose or slides. Name
  the pattern or idiom instead, and keep pointers to other chapters light: each chapter stands alone.
- **No internal codes** (PDP-###, rNN, spike names) and no verification status in reader-facing files.
- Say **"final project"**, never "capstone".
- Parts use Arabic numbering, never Roman numerals.
- **Liquid gotcha**: Jekyll parses `{{ ... }}` inside fenced code. Wrap any Python block that
  contains `{{` (f-strings, dict-in-dict) in `{% raw %}` ... `{% endraw %}`; validate.py checks.

## Voice

- **No em-dashes**, zero tolerance, in prose, captions, plans and comments. No rule-of-three
  padding, no confessional or defensive phrasing, no meta-narration.
- Professional peer-to-peer register. `lgtm-professional-voice` is a gate, not a polish step.
- Prose reviews apply the house-voice rubric plus `scan.sh --stats`, not only the tic scan.
- Reader-facing content has no cross-references to sibling sites inside chapters or decks. The
  series line lives in the README and the site chrome only.

## Example code

- **Shipping domain only** (consignments, carriers, rate quotes, routing, tracking, billing),
  per `_plans/shipping-domain-model.md`. Never `Foo`/`Bar`, shapes or animals. **Zero UI.**
  Do not invent a new domain area; respect the non-overlap assignments between chapters 20/26,
  25/28 and 20/30.
- **Idiomatic modern Python only. Never Java-in-Python.** `Protocol` over interface hierarchies;
  frozen dataclasses; callables and closures; generators; context managers; `functools.singledispatch`;
  `match` with `assert_never`. When a GoF pattern is redundant, say so rather than reproduce it.
  Comparison code is allowed when a comparison teaches something, as the exception, not the norm
  (owner decision 2026-11-04). It must be real, runnable and tested against the same behaviour as
  the idiomatic version (one shared table of cases), so the comparison is a measured result and not
  a strawman, and the chapter teaches the idiomatic code: the comparison sits beside it, briefly,
  and never replaces it. The legacy-code part, where inherited code is the subject, is separate.
- Strict typing is the gate (`mypy --strict`, `warn_unreachable`). Ruff is configured at the root.
- Every example is standalone: `cd examples/<NN-slug> && uv run pytest && uv run mypy --strict src tests`.
- **Deterministic tests.** No `sleep`, wall clock or `perf_counter` in tests. A race is forced by a
  seam: `threading.Barrier`, `threading.Event`, `asyncio.Event`, `asyncio.sleep(0)`, or a hook.
  Assert the exact outcome of the forced interleaving. Performance claims live only in benchmark
  scripts with recorded, host-scrubbed output, never in assertions.
- Tests assert behaviour, not that the build exits 0. Prefer `mocker.create_autospec` and say
  in the prose that mocks bypass the static check.
- Primary sources first: the Python docs, the typing spec and PEPs.

## Spike findings to remember

- **Mocks are assignable to every type, not literally `Any`.** `Mock`, `MagicMock(spec=...)` and
  `create_autospec(..., instance=True)` are all accepted where a Protocol is expected because the
  mock classes subclass `Any` in typeshed (`reveal_type` shows the `MagicMock` union, not `Any`).
  Only autospec enforces the call signature at runtime. `@runtime_checkable` checks names only.
- **`runtime_checkable` is not inherited (3.15).** A Protocol that inherits a runtime-checkable
  Protocol without its own decorator emits a `DeprecationWarning` on `isinstance` and will raise
  `TypeError` in 3.20. `filterwarnings = ["error"]` turns that into a failure.
- **An explicit Protocol subclass disagrees with itself.** mypy reports `[abstract]` on
  instantiating it, the runtime instantiates it, and the inherited `...` body returns `None`.
  State it as observed behaviour.
- **contextlib changed in 3.15.** A `@contextmanager` used as a decorator on a generator function
  now holds the context across iteration. Cite What's New, test only the 3.15 behaviour, and rest
  any "before 3.15" sentence on the source plus the recorded 3.14.10 run.
- **API snippets target the running interpreter, member runs target the root config.** Run a
  `mypy.api` witness from outside the repo so the root `python_version` does not apply, and keep
  both on 3.15.
- Callback Protocols need positional-only `/` or parameter names must match.
- **Pure percentage layers commute** (discount then VAT equals VAT then discount). A Decorator
  "order matters" demo must use an additive fee, a cap or rounding.
- `@audited` must be a factory (`@audited(sink)`). `__wrapped__` needs one `# type: ignore[attr-defined]`.
  Exception names end in `Error` (ruff N818).
- **`break` out of `async for` does not run the async generator's `finally`**: use
  `contextlib.aclosing`, and annotate as `AsyncGenerator`, not `AsyncIterator`.
- **`functools.cache` is not call-once under threads.** For a singleton, build at import time or
  use a Lock with a double check.
- The natural `+=` lost update did not reproduce in 600 runs (measured on 3.14.10): claim it in prose only; force it
  with a `gap=` hook plus `Barrier` for the test.
- `sleep(0)` task order is a CPython implementation detail: say so. Never assert that work
  finishes inside a timeout; `asyncio.timeout(0)` is the deterministic cancellation test.
- uv inside a member does not see the root dev group (see Toolchain); pytest, ruff and mypy
  discover the root config from a member directory.

## Per-chapter gates (before handback)

1. `bash scripts/verify.sh` green.
2. `uv run python scripts/validate.py` exits 0.
3. `lgtm-professional-voice` `scan.sh` to **0 ban-tier** over the chapter, with `--stats` reviewed.
   Repo-wide gate: `bash ~/.claude/skills/lgtm-professional-voice/scripts/scan.sh --tier ban --fail
   --exclude LICENSE-docs.md --exclude CLAUDE.md --exclude validate.py --exclude host_ids.py
   --exclude .venv-ft .` (the first four name the banned patterns or are verbatim legal text;
   `.venv-ft` is the free-threaded environment, which the scanner does not prune).
4. `lgtm-idiomatic-review` scan over the example: 0 ban-tier.
5. `python3 scripts/host_ids.py check` exits 0.
6. Quoted output matches a fresh run modulo scrubbing.

The voice ban scan excludes `LICENSE-docs.md`, which is the verbatim CC BY 4.0 legal text.

## Publishing rule: nothing identifies the machine or its owner

The repo is public, so no tracked file may name the development machine, its owner or anything
that helps locate or attack it later:

- No absolute home-directory path (under /home or /Users), no account name, no hostname. Write
  `<repo>/...` or `~/...`. Scrub `<repo>` in captured output (pytest `rootdir:`, uv, tracebacks).
- No laptop model, no CPU model or model number (a class such as "Intel 8-core/16-thread laptop CPU"
  is fine), no host kernel build or build date (give `major.minor`).
- No machine-id, DMI serial or UUID, MAC or IP address, `root=UUID=` or BOOT_IMAGE.
- Generated output is scrubbed before it is committed: `python3 scripts/host_ids.py scrub <dir>` on
  a results directory, `python3 scripts/host_ids.py filter` on a captured log.
- `python3 scripts/host_ids.py check` runs in CI (`host-ids` job) and fails the build on a hit.
  `scripts/host_ids.py` is vendored unchanged from lgtm-skills; do not edit it here.

## Git and release workflow

- **Never commit directly to `main`.** One `release/rNN` branch and one PR per iteration, with
  checkpoint commits on the branch (Conventional Commits, `type(scope): summary`).
- Squash-merge, delete the branch, tag `rNN.x` on main, publish a **notes-only** GitHub release.
- The `main` ruleset (squash only, required check `ci-ok`) is applied after the first merge so the
  check name exists. CI is `.github/workflows/ci.yml`; `ci-ok` fails unless `python`, `validate`
  and `host-ids` all succeeded.
- Before each release: re-verify pinned versions upstream, update the dated table and `uv.lock`.
- Companion decks are built last: 101, 201, 301.
- Public repo even if a PRD says private. The repo About website link is the Pages URL.

## Relay flow

`lgtm-relay`: Opus plans (reviewed by the owner), Sonnet executors build, Opus validates.
Executor order per chapter: example and tests first (green), then prose quoting real scrubbed
output, then one agent that owns `_data/diagrams.yml`, the specs and the captions. Executors own
only the files they are assigned and never edit plans. Fix defects in the current iteration and
re-measure; defer only content that belongs to a future part.

## Skills to use

`lgtm-python` (toolchain), `lgtm-jekyll` (site), `lgtm-tutorial` (chapter workflow),
`lgtm-diagram-generator` (figures), `lgtm-professional-voice` (voice gate),
`lgtm-idiomatic-review` (Python idiom pass), `lgtm-host-scrub` (publishing rule),
`lgtm-github` (branch, PR, tag, release, ruleset), `lgtm-presentation` (decks),
`lgtm-relay` (plan, execute, validate).

## Dated notes

- 2026-11-04 (r05): Python 3.15.2. The book, pins and floor move from 3.14.10 to 3.15.2 (CPython 3.15.2
  was released 2026-10-25). Measurements taken on 3.14.10 stay labelled as such; the older plans
  (r02 to r04) and the spike findings remain as history.
- 2026-11-08 (r25, decision 7): the six appendix word-floor warnings (appendices A to F: 1,595,
  1,703, 1,880, 1,824, 931 and 1,896 words) are confirmed as owner-accepted. They are not padded
  and not exempted in `validate.py`; the floor stays a warning.
- 2026-11-08 (r25, O2): the owner approved a terse rewording of the whole book (r26 to r28). From
  r26 on, tests are named on a `*Tests:*` line after the paragraph, not inside the sentence, and
  the 1,900-word floor is dropped. The terse register lives in `lgtm-professional-voice`. Until
  r26 changes `validate.py`, the current floor and the test-naming rule still apply.
