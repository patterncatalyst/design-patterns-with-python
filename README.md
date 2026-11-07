# Design Patterns with Python

The GoF patterns and SOLID principles in idiomatic Python 3.15, sorted three ways: patterns the
language dissolves into a callable, a generator or a module; patterns that survive as real design;
and names that need disambiguating. The Decorator pattern and the `@decorator` syntax are the
clearest case. Every example is a tested program in a shipping domain, type-checked with mypy in
strict mode.

Site: https://patterncatalyst.github.io/design-patterns-with-python/

## The series

- [Design Patterns in C++](https://patterncatalyst.github.io/cpp-design-patterns/)
- [Design Patterns with Java](https://patterncatalyst.github.io/design-patterns-with-java/)
- [Design Patterns with .NET / C#](https://patterncatalyst.github.io/csharp-design-patterns/)
- Design Patterns with Python (this book)

## Quick start

Prerequisites: Linux with `bash`, [uv](https://docs.astral.sh/uv/) 0.13 or newer, and `git`. uv
installs the pinned Python 3.15 interpreter on demand.

```bash
bash scripts/check-prereqs.sh          # verify the toolchain
uv sync --locked --all-packages        # one environment for every example
bash scripts/verify.sh                 # lint, format, strict types, tests
```

Each example also runs on its own:

```bash
cd examples/00-prerequisites
uv run pytest
uv run mypy --strict src tests
```

Building the site needs Docker Engine and no local Ruby: `bash scripts/site-build.sh`.

## Layout

| Path | Contents |
| --- | --- |
| `_docs/` | Chapters and appendices |
| `_parts/`, `_examples/` | Part pages and example cards |
| `examples/` | One runnable, tested uv workspace member per chapter |
| `diagrams/` | Figure specs and the generated SVG and Excalidraw pairs |
| `scripts/` | Verification, validation, prerequisite and site-build scripts |
| `.github/workflows/` | CI and Pages deployment |

## Companion decks

- [101: Patterns and SOLID in Python](presentation/design-patterns-with-python-101-patterns-and-solid.pptx):
  62 slides with speaker notes. Code on the slides is read from the tested examples at build time.
  `presentation/build-notes.md` says how to rebuild it.

## Licence

Code is licensed under Apache-2.0 (see `LICENSE`). Prose, diagrams and the slide decks under
`presentation/` are licensed under CC BY 4.0 (see `LICENSE-docs.md`).
