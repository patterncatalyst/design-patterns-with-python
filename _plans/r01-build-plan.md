---
title: "r01 build plan: scaffold + toolchain + Chapter 0 + feature spikes"
order: 1
output: false
---

# r01: Design Patterns with Python scaffold

First iteration of the FOURTH book in the series (C++ ✅, Java ✅, C# ✅).
Source of truth: Notion PRD "Design Patterns with Python" and its "Chapter
Outline & Research Map". Source of truth for r01 scope, acceptance criteria and
status. **Executors never edit this file; the orchestrator updates the status board.**

## User decisions (2026-11-03, binding)

- Repo `design-patterns-with-python`; public; release/rNN branch + PR per iteration.
- Concurrency is TWO asyncio-centred chapters (37 GIL and performance; 38 asyncio and
  the patterns). Book is 41 chapters (0-40) + appendices A-F (docs 41-46).
- Skip free-threaded Python (PEP 703). Do discuss GIL performance impact and its
  relation to async code.
- Hub: "GoF Design Patterns and SOLID Principles" section.
- Accent: **series red `#c0392b`** (same as C++/Java). Diagrams keep house amber.
- Keep "Figure N.1:" prefix on HTML captions; never numbers inside SVGs or body prose.
- EAFP vs LBYL lives in ch31 ("Shortcut patterns: dict dispatch, function tables, and
  EAFP"); Null Object lives in ch9 (`Optional` + mypy making absence explicit).
- Apply the lgtm-github ruleset on `main` after the r01 merge (squash-only, `ci-ok`).
- Jekyll build runs in a `ruby:4.0.x` container under **Docker Engine** (podman is not
  installed on this host). Build tool only; never mentioned in reader pages.

## Approach

Copy site chrome from `csharp-design-patterns` (most refined sibling), cross-checked
against `lgtm-jekyll/assets/site-template`, and fix four C# defects while copying:
1. add an `_examples/` collection (C# Examples page is empty);
2. ship `LICENSE-docs.md` (CC BY 4.0) like Java/C++;
3. no orphan "Figure N.1: TODO caption" placeholders in stubs;
4. `.gitattributes` must NOT mark `*.py` as vendored.

Examples use **one uv workspace** (root `pyproject.toml` + single `uv.lock`), each
example a member runnable from its own directory. Rejected: per-example lockfiles
(~35 locks drifting), one flat package (examples not standalone), generating from the
template (loses C# refinements), Ch0-4 in r01 (too large), spikes in example dirs
(spikes are evidence, not reader code; they live in `spikes/`).

## PDP id scheme

0xx infrastructure · 1NN chapter NN (PDP-100..140) · PDP-141..146 appendices A-F ·
PDP-150..152 decks 101/201/301.

## Steps and status

| Step | PDP | What | Depends | Status |
| --- | --- | --- | --- | --- |
| S0 | 001 | Upstream survey: Python 3.14.x, uv, pytest, pytest-mock, ruff, mypy, uv_build, GH Actions, ruby:4.0.x tag + Jekyll gems, bibliography editions; dated table below | - | **done** |
| S1 | 002 | Repo created remote-first, About = Pages URL, `release/r01` branch | - | **done** |
| S2 | 003 | Site scaffold copied from C# and rewritten for Python; `_config.yml` (examples collection, excludes with trailing slash), red accent, nav, `.gitattributes` | S1 | **done** |
| S3 | 004 | 15 part pages (00-13 + 14-appendices), 47 doc stubs with spine headings, no figure include/TODO, `scripts/chapters.toml` | S2 | **done** |
| S4 | 005 | uv workspace: root pyproject (exact `==` dev pins, ruff py314, mypy strict, pytest importlib), `.python-version`, `uv.lock`, `.gitignore`, `examples/README.md`; gate spike S4a (member dev tools, mypy duplicate modules, config pickup) recorded in `spikes.md` | S0 | **done** (mypy per member) |
| S5 | 006 | scripts: check-prereqs.sh, verify.sh, site-build.sh (docker), validate.py, host_ids.py (+ .host-scrub.toml), generate_diagram.py, render_diagrams.py | S4 | **done** |
| S6 | 010-015 | Six spikes in `spikes/feature-spikes` (pkg `feature_spikes`): Decorator vs @decorator; Protocol/ParamSpec/PEP 695; singledispatch on 3.14; __init_subclass__ vs metaclass; match + assert_never; GIL/asyncio determinism | S4 | **done** (all go) |
| S7 | 100a | `examples/00-prerequisites` (pkg `consignments`): frozen slotted Consignment, ConsignmentId/Weight validation, `replace`; tests assert behaviour | S4 | **done** (26 tests) |
| S8 | 007-009 | `_plans/iteration-plan.md`, `shipping-domain-model.md` (7 domain areas, example per chapter, non-overlap 20/26, 25/28, 20/30), `reconciliation-plan.md`; revise after S6 | - | **done** (revise after S6) |
| S9 | 100b | Ch0 figure spec (vertical flow uv -> .venv -> ruff -> mypy -> pytest), render, `_data/diagrams.yml` | S7 | **done** |
| S10 | 100c | Ch0 prose, 1,900-2,500 words, real scrubbed output, scan.sh 0 ban-tier | S7,S9 | **done** (2013 words) |
| S11 | 016 | `_examples/00-prerequisites.md` card; bibliography (books only, verified) | S0,S7 | **done** (O'Reilly URLs 403 to curl; ISBN form) |
| S12 | 017 | `ci.yml` (python, validate, host-ids, ci-ok), CLAUDE.md, README | S4,S5 | **done** |
| S13 | 018 | Validation wave: every acceptance criterion; fix in-iteration | all | **done** (2 repair rounds; criteria 1-13 met) |
| S14 | 019 | PR, CI green, squash-merge --delete-branch, Pages live, tag r01.x, notes-only release, ruleset | S13 | **done** (PR #1, r01.x, ruleset) |
| S15 | 020 | Hub PR: sites.yml card (GoF section), books.yml + book_categories.yml | S14 | **done** (hub PR #49) |

## Verified toolchain (fill in S0, dated)

| Item | Version | Date checked | Source |
| --- | --- | --- | --- |
| CPython | 3.14.10 (released 2026-10-25) | 2026-11-03 | endoflife.date python 3.14 |
| uv | 0.13.7 (2026-11-03) | 2026-11-03 | github.com/astral-sh/uv/releases |
| uv_build (PyPI `uv-build`) | 0.13.7, pin `>=0.13.7,<0.14` | 2026-11-03 | PyPI |
| pytest | 9.2.0 | 2026-11-03 | PyPI |
| pytest-mock | 3.17.0 | 2026-11-03 | PyPI |
| ruff | 0.17.3 | 2026-11-03 | PyPI |
| mypy | 2.4.1 (supports 3.14) | 2026-11-03 | PyPI |
| actions/checkout | v7 (7.0.1) | 2026-11-03 | GitHub releases |
| astral-sh/setup-uv | v10 (10.3.3) | 2026-11-03 | GitHub releases |
| actions/configure-pages | v6 (6.0.0) | 2026-11-03 | GitHub releases |
| actions/upload-pages-artifact | v5 (5.0.0) | 2026-11-03 | GitHub releases |
| actions/deploy-pages | v5 (5.0.1) | 2026-11-03 | GitHub releases |
| ruby/setup-ruby | v1 (1.336.0), ruby-version 4.0.9 | 2026-11-03 | GitHub releases |
| ruby container (site build) | ruby:4.0.9 | 2026-11-03 | Docker Hub |
| Jekyll + plugins | jekyll 4.4.1, seo-tag 2.9.1, sitemap 1.4.0, redirect-from 0.17.0, sass-converter 3.1.0 (all current); csv 3.3.6 -> bump to 3.3.7 | 2026-11-03 | rubygems.org |

Bibliography (verified via O'Reilly platform 2026-11-03): Fluent Python 2nd ed (2022);
Architecture Patterns with Python (2020); **Effective Python 3rd ed (2024)**, not 2nd;
**Python Object-Oriented Programming 5th ed, Lott & Phillips (Packt, 2025)**. Series
books (GoF, Martin, Feathers, Fowler 2nd, Meszaros) reuse the C# book's URLs.

Host (user-local, no system change): uv upgraded 0.13.5 -> 0.13.7; `uv python install 3.14.10`.

## Release roadmap

| Iter | Content |
| --- | --- |
| r01 | Scaffold, toolchain, CI, plans, domain model, spikes, Chapter 0, hub |
| r02 | Ch 1-4: forces, 1994, three-way-split map, naming |
| r03 | Ch 5-6: SOLID |
| r04 | Ch 7-8: data model, dataclasses |
| r05 | Ch 9-11: Protocol/mypy (+ Null Object), context managers, testing baseline |
| r06 | Ch 12-13: Strategy, Template Method |
| r07 | Ch 14-15: State/FSM, Command/undo |
| r08 | Ch 16-18: factories, Builder/dataclass/Prototype, Singleton |
| r09 | Ch 19-20: Adapter/Facade/Bridge, Decorator vs @decorator + Proxy |
| r10 | Ch 21-22: Composite/Flyweight, Observer |
| r11 | Ch 23-24: Mediator/CoR, Iterator |
| r12 | Ch 25-26: Visitor/Memento/Interpreter, decorators done right |
| r13 | Ch 27-28: descriptors, singledispatch |
| r14 | Ch 29-30: __init_subclass__/metaclasses, __getattr__/Proxy |
| r15 | Ch 31-32: dict dispatch + EAFP, anti-patterns |
| r16 | Ch 33-34: seams, dependency-breaking |
| r17 | Ch 35-36: Fowler vs Feathers, refactor or rewrite |
| r18 | Ch 37-38: the GIL and performance; asyncio and the patterns |
| r19 | Ch 39-40: final project, working with AI and LLM tools |
| r20 | Appendices A-C |
| r21 | Appendices D-F |
| r22-r24 | Decks 101, 201, 301 |
| r25 | Retro and QA sweep |

## Chapter slugs

00-prerequisites · 01-patterns-as-decisions-under-forces ·
02-what-1994-assumed-and-python-dissolves · 03-the-three-way-split ·
04-naming-patterns-for-teams-and-ai · 05-srp-ocp-lsp ·
06-isp-dip-and-di-without-a-framework · 07-the-data-model ·
08-dataclasses-and-value-semantics · 09-protocol-and-structural-typing ·
10-context-managers · 11-testing-with-pytest-pytest-mock-and-mypy ·
12-strategy-the-callable · 13-template-method-and-the-function-alternative ·
14-state-and-finite-state-machines · 15-command-undo-and-command-queues ·
16-factory-method-and-abstract-factory · 17-builder-dataclasses-and-prototype ·
18-singleton-module-borg-metaclass · 19-adapter-facade-bridge ·
20-decorator-pattern-vs-decorator-syntax-and-proxy · 21-composite-and-flyweight ·
22-observer · 23-mediator-and-chain-of-responsibility ·
24-iterator-generators-and-the-iterator-protocol · 25-visitor-memento-interpreter ·
26-decorators-done-right · 27-descriptors-and-properties · 28-singledispatch ·
29-metaclasses-init-subclass-and-registries · 30-dynamic-attributes-and-proxy ·
31-shortcut-patterns-dict-dispatch-and-eafp · 32-anti-patterns-and-pattern-misuse ·
33-seams-in-python · 34-dependency-breaking-techniques · 35-fowler-vs-feathers ·
36-refactor-or-rewrite · 37-the-gil-and-performance · 38-asyncio-and-the-patterns ·
39-final-project · 40-working-with-ai-and-llm-tools · 41..46 appendix-a..appendix-f

## Acceptance criteria

1. `gh repo view` reports PUBLIC + Pages homepage; work on `release/r01`, deleted after merge.
2. Fresh clone, root: `uv sync --locked --all-packages`, `uv run ruff check .`,
   `uv run ruff format --check .`, `uv run mypy --strict` (per S4a), `uv run pytest` all exit 0.
3. `examples/00-prerequisites`: `uv run pytest` and `uv run mypy --strict src tests` exit 0;
   tests assert equality, hash, `replace` immutability, invalid-input rejection.
4. `spikes/feature-spikes` passes 3x consecutively; no `time.sleep|time.time(|perf_counter`
   in spike tests; `_plans/spikes.md` has go/adjust/no-go per spike; decorator spike shows
   both mechanisms in shipping types.
5. `scripts/check-prereqs.sh` exits 0 on host; non-zero with uv stripped from PATH.
6. All dev deps `==`; `.python-version` exact 3.14.x; version table matches `uv.lock` and
   Chapter 0 (validate.py checks).
7. `scripts/site-build.sh` succeeds: `_site/docs` = 48 entries, `_site/parts` = 15,
   `_site/examples/00-prerequisites/index.html` exists, index pages non-empty, no
   pyproject/uv.lock/spikes/scripts/diagrams/specs in `_site`; `git status` clean after.
8. `uv run python scripts/validate.py` exits 0.
9. lgtm-professional-voice `scan.sh --tier ban --fail` over reader-facing files exits 0;
   `--stats` reviewed for Chapter 0.
10. lgtm-idiomatic-review scan over `examples/` and `spikes/`: 0 ban-tier, or each survivor kept
    for a reason recorded in `_plans/spikes.md` (the GIL benchmark's `print()` report is kept).
11. `python3 scripts/host_ids.py check` exits 0; no home path or account name tracked.
12. Chapter 0: >= 1,900 words, full spine, one figure include with 20-45 word caption,
    no em-dashes, dated pin table, quoted output matches a fresh run modulo scrubbing.
13. No C# leftovers in chrome/_config (`dotnet|\.NET|C#|xUnit|NSubstitute|csharp|#512bd4`)
    except the README series line.
14. CI `ci-ok` green on PR; Pages deployed; `r01.x` on merged main; release notes-only;
    ruleset active on `main`.
15. Hub PR merged; live hub shows the Python card in the GoF section.

## Risks

- Member dirs lack dev tools on fresh clone (S4a; per-member dev groups if needed).
- mypy duplicate-module / pytest basename collisions across examples (S4a, importlib mode).
- Liquid eats Python braces (validate.py fenced-block check + real build).
- Host paths leak via pytest `rootdir:`/uv/tracebacks (host_ids.py in CI, scrub filter).
- Concurrency claims flaky or timing-based (PDP-015 decides; perf claims go in scrubbed
  benchmark output, never assertions).
- mypy lags 3.14 features (spikes 011/012/014).
- Overlapping chapters 20/26, 25/28, 20/30 (domain model assigns non-overlapping examples).
- Copied chrome keeps .NET wording or purple (criterion 13).
- Container build mutates Gemfile.lock (BUNDLE_FROZEN, git status check).
- Fabricated bibliography editions (S0 verifies; unverifiable dropped).
