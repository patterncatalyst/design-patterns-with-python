---
title: "Iteration plan and PDP registry"
order: 7
output: false
---

# PDP-007: iteration plan and registry

Internal planning file, excluded from the site. Scheme: 001-020 infrastructure,
100-140 chapters 0-40 (suffix a = example, b = figure, c = prose), 141-146
appendices A-F, 150-152 decks 101/201/301. Status values: todo, active, done.
The orchestrator updates status; executors do not edit `r01-build-plan.md`.

Each iteration follows the same shape as the C# book: a `release/rNN` branch, one
PR, squash-merge with branch deletion, an `rNN.x` tag and a notes-only release.

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
| r10b | Retrofit chapters 0-20 to lgtm-professional-voice #94-#96 (owner decision 2026-11-05): AI sidebars to problem + ready-to-paste prompt + one review line; objective-payoff closers; intent-before-mechanism and no re-narrated code where a chapter falls short. Its own plan, validation and PR |
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
| r21 (active) | Appendices D-F |
| r22-r24 | Decks 101, 201, 301 |
| r25 | Retro and QA sweep |

## Registry

| ID | Item | Iteration | Status |
| --- | --- | --- | --- |
| PDP-001 | Upstream survey (versions, bibliography editions) | r01 | todo |
| PDP-002 | Repo created, Pages homepage, release/r01 branch | r01 | done |
| PDP-003 | Site scaffold (chrome, _config, red accent) | r01 | todo |
| PDP-004 | 15 parts plus 47 doc stubs, chapters.toml | r01 | todo |
| PDP-005 | uv workspace toolchain (S4a gate spike) | r01 | todo |
| PDP-006 | Scripts: prereqs, verify, site-build, validate, host_ids, diagrams | r01 | todo |
| PDP-007 | Iteration plan and registry (this file) | r01 | todo |
| PDP-008 | Shipping domain model | r01 | todo |
| PDP-009 | Reconciliation plan | r01 | todo |
| PDP-010 | Spike 010: Decorator objects vs @decorator | r01 | todo |
| PDP-011 | Spike 011: Protocol, ParamSpec, PEP 695 | r01 | todo |
| PDP-012 | Spike 012: singledispatch on 3.14 | r01 | todo |
| PDP-013 | Spike 013: __init_subclass__ vs metaclass | r01 | todo |
| PDP-014 | Spike 014: match and assert_never | r01 | todo |
| PDP-015 | Spike 015: GIL and asyncio determinism | r01 | todo |
| PDP-016 | Examples card and verified bibliography | r01 | todo |
| PDP-017 | CI, CLAUDE.md, README | r01 | todo |
| PDP-018 | Validation wave | r01 | todo |
| PDP-019 | Ship: PR, CI, merge, tag, release, ruleset | r01 | todo |
| PDP-020 | Hub PR: sites.yml, books.yml, book_categories.yml | r01 | todo |
| PDP-100a | Ch0 Prerequisites and the toolchain: example | r01 | todo |
| PDP-100b | Ch0 Prerequisites and the toolchain: figure | r01 | todo |
| PDP-100c | Ch0 Prerequisites and the toolchain: prose | r01 | todo |
| PDP-101a | Ch1 Patterns as decisions under forces: example | r02 | n.a. (argument chapter) |
| PDP-101b | Ch1 Patterns as decisions under forces: figure | r02 | todo |
| PDP-101c | Ch1 Patterns as decisions under forces: prose | r02 | todo |
| PDP-102a | Ch2 What 1994 assumed, and what Python dissolves: example | r02 | covered by PDP-103a |
| PDP-102b | Ch2 What 1994 assumed, and what Python dissolves: figure | r02 | todo |
| PDP-102c | Ch2 What 1994 assumed, and what Python dissolves: prose | r02 | todo |
| PDP-103a | Ch3 The three-way split: example (three-way-split witnesses) | r02 | todo |
| PDP-103b | Ch3 The three-way split: figure | r02 | todo |
| PDP-103c | Ch3 The three-way split: prose | r02 | todo |
| PDP-104a | Ch4 Naming patterns for teams and AI: example | r02 | n.a. (argument chapter) |
| PDP-104b | Ch4 Naming patterns for teams and AI: figure | r02 | todo |
| PDP-104c | Ch4 Naming patterns for teams and AI: prose | r02 | todo |
| PDP-105a | Ch5 SRP, OCP, and LSP: example | r03 | active |
| PDP-105b | Ch5 SRP, OCP, and LSP: figure | r03 | active |
| PDP-105c | Ch5 SRP, OCP, and LSP: prose | r03 | active |
| PDP-106a | Ch6 ISP, DIP, and DI without a framework: example | r03 | active |
| PDP-106b | Ch6 ISP, DIP, and DI without a framework: figure | r03 | active |
| PDP-106c | Ch6 ISP, DIP, and DI without a framework: prose | r03 | active |
| PDP-107a | Ch7 The data model: example | r04 | active |
| PDP-107b | Ch7 The data model: figure | r04 | active |
| PDP-107c | Ch7 The data model: prose | r04 | active |
| PDP-108a | Ch8 Dataclasses and value semantics: example | r04 | active |
| PDP-108b | Ch8 Dataclasses and value semantics: figure | r04 | active |
| PDP-108c | Ch8 Dataclasses and value semantics: prose | r04 | active |
| PDP-109a | Ch9 Protocol and structural typing: example | r05 | active |
| PDP-109b | Ch9 Protocol and structural typing: figure | r05 | active |
| PDP-109c | Ch9 Protocol and structural typing: prose | r05 | active |
| PDP-110a | Ch10 Context managers: example | r05 | active |
| PDP-110b | Ch10 Context managers: figure | r05 | active |
| PDP-110c | Ch10 Context managers: prose | r05 | active |
| PDP-111a | Ch11 Testing with pytest, pytest-mock, and mypy: example | r05 | active |
| PDP-111b | Ch11 Testing with pytest, pytest-mock, and mypy: figure | r05 | active |
| PDP-111c | Ch11 Testing with pytest, pytest-mock, and mypy: prose | r05 | active |
| PDP-112a | Ch12 Strategy: the callable: example | r06 | active |
| PDP-112b | Ch12 Strategy: the callable: figure | r06 | active |
| PDP-112c | Ch12 Strategy: the callable: prose | r06 | active |
| PDP-113a | Ch13 Template Method and the function alternative: example | r06 | active |
| PDP-113b | Ch13 Template Method and the function alternative: figure | r06 | active |
| PDP-113c | Ch13 Template Method and the function alternative: prose | r06 | active |
| PDP-114a | Ch14 State and finite state machines: example | r07 | active |
| PDP-114b | Ch14 State and finite state machines: figure | r07 | active |
| PDP-114c | Ch14 State and finite state machines: prose | r07 | active |
| PDP-115a | Ch15 Command, undo, and command queues: example | r07 | active |
| PDP-115b | Ch15 Command, undo, and command queues: figure | r07 | active |
| PDP-115c | Ch15 Command, undo, and command queues: prose | r07 | active |
| PDP-116a | Ch16 Factory Method and Abstract Factory: example | r08 | active |
| PDP-116b | Ch16 Factory Method and Abstract Factory: figure | r08 | active |
| PDP-116c | Ch16 Factory Method and Abstract Factory: prose | r08 | active |
| PDP-117a | Ch17 Builder, dataclasses, and Prototype: example | r08 | active |
| PDP-117b | Ch17 Builder, dataclasses, and Prototype: figure | r08 | active |
| PDP-117c | Ch17 Builder, dataclasses, and Prototype: prose | r08 | active |
| PDP-118a | Ch18 Singleton: module, Borg, metaclass: example | r08 | active |
| PDP-118b | Ch18 Singleton: module, Borg, metaclass: figure | r08 | active |
| PDP-118c | Ch18 Singleton: module, Borg, metaclass: prose | r08 | active |
| PDP-119a | Ch19 Adapter, Facade, Bridge: example | r09 | active |
| PDP-119b | Ch19 Adapter, Facade, Bridge: figure | r09 | active |
| PDP-119c | Ch19 Adapter, Facade, Bridge: prose | r09 | active |
| PDP-120a | Ch20 Decorator pattern vs decorator syntax, and Proxy: example | r09 | active |
| PDP-120b | Ch20 Decorator pattern vs decorator syntax, and Proxy: figure | r09 | active |
| PDP-120c | Ch20 Decorator pattern vs decorator syntax, and Proxy: prose | r09 | active |
| PDP-121a | Ch21 Composite and Flyweight: example | r10 | done |
| PDP-121b | Ch21 Composite and Flyweight: figure | r10 | done |
| PDP-121c | Ch21 Composite and Flyweight: prose | r10 | done |
| PDP-122a | Ch22 Observer: example | r10 | done |
| PDP-122b | Ch22 Observer: figure | r10 | done |
| PDP-122c | Ch22 Observer: prose | r10 | done |
| PDP-123a | Ch23 Mediator and Chain of Responsibility: example | r11 | done |
| PDP-123b | Ch23 Mediator and Chain of Responsibility: figure | r11 | done |
| PDP-123c | Ch23 Mediator and Chain of Responsibility: prose | r11 | done |
| PDP-124a | Ch24 Iterator, generators, and the iterator protocol: example | r11 | done |
| PDP-124b | Ch24 Iterator, generators, and the iterator protocol: figure | r11 | done |
| PDP-124c | Ch24 Iterator, generators, and the iterator protocol: prose | r11 | done |
| PDP-125a | Ch25 Visitor, Memento, Interpreter: example | r12 | done |
| PDP-125b | Ch25 Visitor, Memento, Interpreter: figure | r12 | done |
| PDP-125c | Ch25 Visitor, Memento, Interpreter: prose | r12 | done |
| PDP-126a | Ch26 Decorators done right: example | r12 | done |
| PDP-126b | Ch26 Decorators done right: figure | r12 | done |
| PDP-126c | Ch26 Decorators done right: prose | r12 | done |
| PDP-127a | Ch27 Descriptors and properties: example | r13 | done |
| PDP-127b | Ch27 Descriptors and properties: figure | r13 | done |
| PDP-127c | Ch27 Descriptors and properties: prose | r13 | done |
| PDP-128a | Ch28 singledispatch: example | r13 | done |
| PDP-128b | Ch28 singledispatch: figure | r13 | done |
| PDP-128c | Ch28 singledispatch: prose | r13 | done |
| PDP-129a | Ch29 Metaclasses, __init_subclass__, and registries: example | r14 | done |
| PDP-129b | Ch29 Metaclasses, __init_subclass__, and registries: figure | r14 | done |
| PDP-129c | Ch29 Metaclasses, __init_subclass__, and registries: prose | r14 | done |
| PDP-130a | Ch30 Dynamic attributes and Proxy: example | r14 | done |
| PDP-130b | Ch30 Dynamic attributes and Proxy: figure | r14 | done |
| PDP-130c | Ch30 Dynamic attributes and Proxy: prose | r14 | done |
| PDP-131a | Ch31 Shortcut patterns: dict dispatch and EAFP: example | r15 | done |
| PDP-131b | Ch31 Shortcut patterns: dict dispatch and EAFP: figure | r15 | done |
| PDP-131c | Ch31 Shortcut patterns: dict dispatch and EAFP: prose | r15 | done |
| PDP-132a | Ch32 Anti-patterns and pattern misuse: example | r15 | done |
| PDP-132b | Ch32 Anti-patterns and pattern misuse: figure | r15 | done |
| PDP-132c | Ch32 Anti-patterns and pattern misuse: prose | r15 | done |
| PDP-133a | Ch33 Seams in Python: example | r16 | done |
| PDP-133b | Ch33 Seams in Python: figure | r16 | done |
| PDP-133c | Ch33 Seams in Python: prose | r16 | done |
| PDP-134a | Ch34 Dependency-breaking techniques: example | r16 | done |
| PDP-134b | Ch34 Dependency-breaking techniques: figure | r16 | done |
| PDP-134c | Ch34 Dependency-breaking techniques: prose | r16 | done |
| PDP-135a | Ch35 Fowler vs Feathers: example | r17 | done |
| PDP-135b | Ch35 Fowler vs Feathers: figure | r17 | done |
| PDP-135c | Ch35 Fowler vs Feathers: prose | r17 | done |
| PDP-136a | Ch36 Refactor or rewrite: example | r17 | done |
| PDP-136b | Ch36 Refactor or rewrite: figure | r17 | done |
| PDP-136c | Ch36 Refactor or rewrite: prose | r17 | done |
| PDP-137a | Ch37 The GIL and performance: example | r18 | done |
| PDP-137b | Ch37 The GIL and performance: figure | r18 | done |
| PDP-137c | Ch37 The GIL and performance: prose | r18 | done |
| PDP-138a | Ch38 asyncio and the patterns: example | r18 | done |
| PDP-138b | Ch38 asyncio and the patterns: figure | r18 | done |
| PDP-138c | Ch38 asyncio and the patterns: prose | r18 | done |
| PDP-139a | Ch39 Final project: example | r19 | done |
| PDP-139b | Ch39 Final project: figure | r19 | done |
| PDP-139c | Ch39 Final project: prose | r19 | done |
| PDP-140a | Ch40 Working with AI and LLM tools: example | r19 | done |
| PDP-140b | Ch40 Working with AI and LLM tools: figure | r19 | done |
| PDP-140c | Ch40 Working with AI and LLM tools: prose | r19 | done |
| PDP-141 | Appendix A: Build and toolchain reference (uv, ruff, mypy) | r20 | done |
| PDP-142 | Appendix B: pytest reference | r20 | done |
| PDP-143 | Appendix C: pytest-mock and unittest.mock reference | r20 | done |
| PDP-144 | Appendix D: Test patterns (Meszaros) | r21 | active |
| PDP-145 | Appendix E: Pattern-to-force quick reference | r21 | active |
| PDP-146 | Appendix F: Programming principles reviewed in code | r21 | active |
| PDP-150 | Deck 101 | r22 | todo |
| PDP-151 | Deck 201 | r23 | todo |
| PDP-152 | Deck 301 | r24 | todo |

2026-11-04 (r05): Python 3.15.2. PDP-109a to PDP-111c are active for r05, and the book moves to Python 3.15.2. Earlier iterations keep their status.

2026-11-04 (r06): PDP-112a to PDP-113c are active for r06 (chapters 12 and 13, Part 5). Earlier iterations keep their status.

2026-11-04 (r07): PDP-114a to PDP-115c are active for r07 (chapters 14 and 15, Part 5). Earlier iterations keep their status.

2026-11-04 (r08): PDP-116a to PDP-118c are active for r08 (chapters 16 to 18, Part 6). Earlier iterations keep their status.

2026-11-04 (r09): PDP-119a to PDP-120c are active for r09 (chapters 19 and 20, Part 7). Earlier iterations keep their status.

2026-11-05 (r10): PDP-121a to PDP-122c are active for r10 (chapters 21 and 22, Parts 7 and 8). Earlier iterations keep their status.

2026-11-05 (r11): PDP-123a to PDP-124c are active for r11 (chapters 23 and 24, Part 8). PDP-121a to PDP-122c are closed (r10 and r10b are tagged), r10b is closed and r11 is marked active in the roadmap. Earlier iterations keep their status.

2026-11-05 (r12): PDP-125a to PDP-126c are active for r12 (chapters 25 and 26, Parts 8 and 9). PDP-123a to PDP-124c are closed (r11 is tagged), r11 is closed and r12 is marked active in the roadmap. Earlier iterations keep their status.

2026-11-06 (r13): PDP-127a to PDP-128c are active for r13 (chapters 27 and 28, Part 9). PDP-125a to PDP-126c are closed (r12 is tagged), r12 is closed and r13 is marked active in the roadmap. Earlier iterations keep their status.

2026-11-06 (r14): PDP-129a to PDP-130c are active for r14 (chapters 29 and 30, Part 9). PDP-127a to PDP-128c are closed (r13 is tagged), r13 is closed and r14 is marked active in the roadmap. Earlier iterations keep their status.

2026-11-06 (r15): PDP-131a to PDP-132c are active for r15 (chapters 31 and 32, Part 10). PDP-129a to PDP-130c are closed (r14 is tagged), r14 is closed and r15 is marked active in the roadmap. Earlier iterations keep their status.

2026-11-06 (r16): PDP-133a to PDP-134c are active for r16 (chapters 33 and 34, Part 11). PDP-131a to PDP-132c are closed (r15 is tagged), r15 is closed and r16 is marked active in the roadmap. Earlier iterations keep their status.

2026-11-06 (r17): PDP-135a to PDP-136c are active for r17 (chapters 35 and 36, Part 11). PDP-133a to PDP-134c are closed (r16 is tagged), r16 is closed and r17 is marked active in the roadmap. Earlier iterations keep their status.

2026-11-06 (r18): PDP-137a to PDP-138c are active for r18 (chapters 37 and 38, Part 12). PDP-135a to PDP-136c are closed (r17 is tagged), r17 is closed and r18 is marked active in the roadmap. Earlier iterations keep their status.

2026-11-07 (r19): PDP-139a to PDP-140c are active for r19 (chapters 39 and 40, Part 13). PDP-137a to PDP-138c are closed (r18 is merged as 3722ab8 and tagged r18.x), r18 is closed and r19 is marked active in the roadmap. Earlier iterations keep their status.

2026-11-07 (r20): PDP-141 to PDP-143 are active for r20 (appendices A to C, Part 14). PDP-139a to PDP-140c are closed (r19 is merged as 95f965d and tagged r19.x), r19 is closed and r20 is marked active in the roadmap. Earlier iterations keep their status.

2026-11-07 (r21): PDP-144 to PDP-146 are active for r21 (appendices D to F, Part 14). PDP-141 to PDP-143 are closed (r20 is merged as 97207d4 and tagged r20.x), r20 is closed and r21 is marked active in the roadmap. Earlier iterations keep their status.
