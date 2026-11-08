---
title: "Context managers: deterministic cleanup"
order: 10
layout: tutorial
sectionid: docs
part: "python-substrate"
description: "The with statement runs __exit__ on every path out of a block, which removes the boilerplate of Resource Acquisition; what release means, whether an exception propagates and the order across resources stay with the author."
---

## Learning objectives

By the end of this chapter you can:

- Say what `with` guarantees, and name the three decisions it leaves to the author: what release means, whether an exception propagates, and the order across several resources.
- Write a context manager as a class and as a `@contextmanager` generator, and say why the generator form needs `try`.
- Combine several resources on an `ExitStack` and predict the order they unwind in.
- Say what a truthy `__exit__` return does and how mypy's reachability analysis reads the return type.
- Say how a context manager used as a decorator changed in Python 3.15.

## Why this matters

A sailing manifest lists the consignments loaded for one port. A job writes it line by line, and halfway through the write the disk fills. Two things go wrong at once. The file handle stays open, because the code that would close it sits after the line that raised. And a half-written manifest sits at the path a downstream reader polls, and that reader takes it for complete: it books the first forty consignments and never hears about the rest.

The first failure is a leak and the second is a lie. Both come from the same gap. Acquiring a resource and releasing it are two steps in different places, and an exception can fall between them. Python closes the gap with the `with` statement. The statement doesn't decide what release should do, and a manifest needs more than `close()`.

{% include excalidraw.html name="10-context-managers" caption="Figure 10.1: Both ways out of a manifest write. After __enter__ opens path.partial, the body writes lines; __exit__ then replaces the partial with path on success, or unlinks it and lets the exception propagate." %}

Read the figure from the top. The accent box is the `with ManifestWriter(path) as out:` line. `__enter__` opens `path.partial`, and the body writes lines to the partial file. The flow then forks. On the left the body returns, so `__exit__(None, None, None)` closes the file and replaces the partial with `path`, and the manifest is committed. On the right the body raises, so `__exit__(exc_type, exc, traceback)` closes the file, unlinks the partial and returns `None`, and the exception propagates.

## Resource Acquisition: the force and why it survives

"Resource acquisition" is the label this book uses for a recurring design problem, and it is descriptive, not a catalogue name. The force: a resource obtained in one place must be released on every path out of the code that uses it, and what release means is a decision. Closing a handle is one answer. Committing a staged file is another. Discarding a half-finished result is a third.

[PEP 343](https://peps.python.org/pep-0343/), by Guido van Rossum and Alyssa Coghlan, added the `with` statement in Python 2.5 to take the acquire-and-release boilerplate out of call sites. The Python Language Reference describes the protocol in its section on [with statement context managers](https://docs.python.org/3.15/reference/datamodel.html#with-statement-context-managers): `__enter__` runs on the way in, and `__exit__` receives the exception details, or three `None` values when the block finished normally. The standard library's [`contextlib` documentation](https://docs.python.org/3.15/library/contextlib.html) covers the helpers used below. For the design side, Michael Kircher and Prashant Jain's *Pattern-Oriented Software Architecture, Volume 3: Patterns for Resource Management* (2004) treats acquiring and releasing resources as a design topic in its own right.

This pattern survives. The language removes the call-site boilerplate: nobody writes `try`/`finally` around every use any more. A feature resolves part of the force and not the rest, because three decisions remain with whoever writes the context manager:

- what release means: close, commit or discard;
- whether an exception propagates or is swallowed;
- the order of release across several resources.

## A class with `__enter__` and `__exit__`

A manifest should appear whole or not at all, so `ManifestWriter` writes to `<name>.partial` and commits to `<name>` only if the block succeeds:

<!-- fmt:off -->
```python
    def __enter__(self) -> TextIO:
        if self._entered:
            raise RuntimeError("ManifestWriter is single-use")
        self._entered = True
        self._handle = self._opener(self._partial)
        return self._handle

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._handle is None:
            raise RuntimeError("ManifestWriter was not entered")
        if exc_type is None:
            self._handle.close()
            self._partial.replace(self._path)
        else:
            self._handle.close()
            self._partial.unlink(missing_ok=True)
```
<!-- fmt:on -->

`Path.replace` is how a reader comes to see the whole manifest or none of it. `test_without_with_an_exception_leaves_the_handle_open` is the control: it opens a file with no `with`, raises mid-write and asserts that the handle is still open afterwards. `test_writer_closes_and_discards_on_an_exception` runs the same failure through `ManifestWriter` and checks that the handle is closed, that neither the partial nor the final file exists, and that the `OSError` reached the caller. `test_writer_commits_only_on_success` checks the other side: inside the block the final path is absent and the partial exists, and after the block the final file holds the written line and the partial is gone.

`__exit__` returns `None`, so the exception continues past the block. The Language Reference says that if the method "wishes to suppress the exception (i.e., prevent it from being propagated), it should return a true value. Otherwise, the exception will be processed normally upon exit from this method." Returning nothing is the decision to let the failure be seen.

Two guards cover misuse. `test_writer_is_single_use` enters the same writer twice and gets `RuntimeError` on the second entry, with one open in total. `test_exiting_a_writer_that_was_never_entered_is_refused` calls `__exit__` directly and gets `was not entered`. The writer takes an `opener` callable, so the tests substitute one that records opens and closes. `open_utf8` passes `encoding="utf-8"` explicitly. Python 3.15 makes UTF-8 the default text encoding ([PEP 686](https://peps.python.org/pep-0686/), listed in [What's New in Python 3.15](https://docs.python.org/3.15/whatsnew/3.15.html)), and writing it out states the intent at the call site.

mypy reads the return type of `__exit__`, because that type tells it whether the block can swallow an exception. `test_mypy_reads_exit_return_type_for_reachability` checks a snippet in which the body of the `with` always raises and the next statement is a `return`:

<!-- fmt:off -->
```python
def write(path: Path) -> int:
    with ManifestWriter(path) as out:
        raise ValueError(out.name)
    return 1
```
<!-- fmt:on -->

With `--strict --warn-unreachable` and `__exit__` annotated `-> None`, mypy 2.4.1 exits with status 1 and prints:

```text
<string>:10: error: Statement is unreachable  [unreachable]
```

The same function over a manager whose `__exit__` is annotated `-> bool` exits 0 with no output, because that manager might swallow the exception and execution might reach the `return`. `test_mypy_types_the_with_target` adds that `out` is a `TextIO` for the class, the generator form and an `ExitStack`.

## The generator form

`@contextmanager` turns a generator into a context manager: the code before `yield` is `__enter__`, and the code after it is `__exit__`. The generator holds the same decisions in less space. Generators as a language feature belong to the chapter titled [Iterator: generators and the iterator protocol]({{ '/docs/24-iterator-generators-and-the-iterator-protocol/' | relative_url }}); here the generator is only a way to write a manager:

<!-- fmt:off -->
```python
@contextmanager
def manifest_file(path: Path, *, opener: Opener = open_utf8) -> Iterator[TextIO]:
    """The same contract as `ManifestWriter`, written as a generator."""
    partial = _partial(path)
    handle = opener(partial)
    try:
        yield handle
    except BaseException:
        handle.close()
        partial.unlink(missing_ok=True)
        raise
    else:
        handle.close()
        partial.replace(path)
```
<!-- fmt:on -->

The `contextlib` documentation says: "If an unhandled exception occurs in the block, it is reraised inside the generator at the point where the yield occurred." That's why `try` isn't optional. Without it, the lines after `yield` are skipped when the block raises, and the close and the discard never run. The class form can't have this bug, since `__exit__` is called on every path by construction. The test fixture `_leaky_manifest_file` is the same generator minus the `try`, and `test_the_generator_form_needs_try` shows the result: after a mid-write `OSError` the handle is still open and the partial file is still on disk. `test_mypy_cannot_see_a_missing_try` type-checks a generator with the same missing `try` under `--strict` and gets exit status 0 with empty output. The type checker has nothing to say, so a test that raises mid-write is the only guard. Both forms run through the same parametrised tests, so `test_writer_closes_and_discards_on_an_exception[class]` and `[generator]` show the contracts match.

The annotation is `Iterator[TextIO]`, and `as out` receives the yielded handle.

## Several resources: ExitStack

One manifest per destination port means several writers, and the question is what happens when the third fails to open. Nesting three `with` statements doesn't scale to a list of unknown length, so `write_manifests` uses an `ExitStack`:

<!-- fmt:off -->
```python
def write_manifests(
    manifests: Iterable[Manifest], directory: Path, *, opener: Opener = open_utf8
) -> list[Path]:
    """Write one manifest per entry: a failed open discards the partials of every writer entered."""
    paths: list[Path] = []
    with ExitStack() as stack:
        for manifest in manifests:
            path = directory / f"{manifest.sailing}-{manifest.port}.manifest"
            out = stack.enter_context(ManifestWriter(path, opener=opener))
            out.writelines(render_line(c) for c in manifest.consignments)
            paths.append(path)
    return paths
```
<!-- fmt:on -->

The [`ExitStack` documentation](https://docs.python.org/3.15/library/contextlib.html) says each instance "maintains a stack of registered callbacks that are called in reverse order when the instance is closed", which is the order a nest of `with` statements would unwind in: the last resource acquired is the first released. `test_exit_stack_unwinds_entered_writers_in_reverse_order` makes the opener fail on the third call. The recorded opens are the first and second partials, and the recorded closes are the second and then the first. The directory ends up empty, because each writer's `__exit__` saw the exception and discarded its partial. The writers decide what release means, and the stack decides the order.

The function docstring states the contract, and it's a narrow one: a failed open discards the partials of every writer entered. `test_exit_stack_commits_every_manifest_on_success` checks the success path: three files committed, no partials. On success each writer commits on its own as the stack unwinds, so the contract says nothing about a failure at commit time.

## Swallowing an exception

A truthy `__exit__` return swallows the exception, and execution continues after the `with`. `test_a_truthy_exit_swallows_the_exception` uses a fixture manager that returns `True`, raises `ValueError` inside the block and then reaches the statement after it. Nothing in the output says an error occurred.

Sometimes that is the intent: a cache file that may not exist yet, a cleanup of something already cleaned. `contextlib.suppress` states it narrowly. `test_suppress_swallows_only_the_named_exception` suppresses `KeyError`, which is swallowed, and then raises `ValueError` inside the same kind of block, which propagates. The documentation for [`suppress`](https://docs.python.org/3.15/library/contextlib.html) says it "should be used only to cover very specific errors where silently continuing with program execution is known to be the right thing to do." Use it where the suppressed case is expected and the code after the block is valid either way. A hand-written `__exit__` that returns `True` to "keep the job going" turns every failure in the block into a success, including the ones nobody anticipated.

## A context manager as a decorator

A context manager built with `@contextmanager` can also be applied as a decorator, because it derives from `ContextDecorator`. That's the `@decorator` syntax, a function rebinding at definition time, applied here to cleanup. The Decorator pattern, objects that wrap objects and compose behaviour at runtime, is a different thing, and the chapter titled [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}) keeps the two apart.

Python 3.15 changed what this does for generator functions. The [What's New in Python 3.15](https://docs.python.org/3.15/whatsnew/3.15.html) entry for `contextlib` reads: "`ContextDecorator` and `AsyncContextDecorator` (and therefore `contextmanager()` and `asynccontextmanager()` used as decorators) now detect generator functions, coroutine functions, and asynchronous generator functions and keep the context manager open across iteration or await. Previously the context manager exited as soon as the generator or coroutine object was created." `test_a_context_manager_decorating_a_generator_spans_iteration` witnesses the 3.15 behaviour:

<!-- fmt:off -->
```python
    @contextmanager
    def scope() -> Iterator[None]:
        log.append("enter")
        try:
            yield
        finally:
            log.append("exit")

    @scope()
    def rows() -> Iterator[str]:
        for port in ("NLRTM", "SGSIN"):
            log.append(f"row {port}")
            yield port
```
<!-- fmt:on -->

Calling `rows()` leaves the log empty. Iterating it produces `["enter", "row NLRTM", "row SGSIN", "exit"]`: the scope opens when iteration starts and closes when it ends. For the "before" half, the source above is the authority, and a recorded run backs it. The same snippet, run with `python -I` on the latest 3.14 release, printed `['enter', 'exit']` before any iteration and `['enter', 'exit', 'row NLRTM', 'row SGSIN']` after it. The scope had already exited by the time the first row was produced. On 3.15.2 it printed an empty log before iteration and the ordering above after it. The test asserts only the 3.15 behaviour. On any code that has to run on both, decide where the scope belongs and write a `with` inside the generator, which behaves the same way on both. The `async with` counterpart of all this is in the chapter titled [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}).

## When not to use it

A resource with no release step doesn't need a manager. A value computed and returned has nothing to acquire. A manager wrapped around a single call that already closes its own resource, such as `Path.read_text`, adds a block and nothing else. Swallowing to "keep going" belongs in `suppress` with one named exception, or in an explicit `try`/`except` at the place that knows how to recover.

<blockquote class="ai-sidebar" markdown="1">
**Specifying cleanup.** "Write the manifest to disk" leaves open when the final path is replaced, what happens on failure and who closes the handle. Paste a prompt that states the contract:

> Write `ManifestWriter` to write `<name>.partial`, close on every path, replace the final path only on success and delete the partial on failure, with `__exit__` returning `None`. In the `@contextmanager` form, wrap the `yield` in `try`/`except`/`else`. Open several writers on an `ExitStack`. Swallow only a named exception, with `contextlib.suppress`. Add a test that raises mid-write and asserts the handle is closed.

If the generator form has no `try`, ask for that test run against it.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then change into the example directory:

```bash
cd examples/10-context-managers
uv run pytest -v
uv run mypy --strict src tests
```

A fresh run produces:

```text
============================= test session starts ==============================
platform linux -- Python 3.15.2, pytest-9.2.0, pluggy-1.7.0 -- <repo>/.venv/bin/python
cachedir: .pytest_cache
rootdir: <repo>
configfile: pyproject.toml
plugins: mock-3.17.0
collecting ... collected 25 items

tests/test_semantics.py::test_a_truthy_exit_swallows_the_exception PASSED [  4%]
tests/test_semantics.py::test_suppress_swallows_only_the_named_exception PASSED [  8%]
tests/test_semantics.py::test_a_context_manager_decorating_a_generator_spans_iteration PASSED [ 12%]
tests/test_semantics.py::test_manifest_rejects_a_port_that_is_not_a_locode[nlrtm] PASSED [ 16%]
tests/test_semantics.py::test_manifest_rejects_a_port_that_is_not_a_locode[NLRT] PASSED [ 20%]
tests/test_semantics.py::test_manifest_rejects_a_port_that_is_not_a_locode[NLRTMX] PASSED [ 24%]
tests/test_semantics.py::test_manifest_rejects_a_port_that_is_not_a_locode[NL-TM] PASSED [ 28%]
tests/test_semantics.py::test_manifest_rejects_a_port_that_is_not_a_locode[] PASSED [ 32%]
tests/test_semantics.py::test_manifest_accepts_a_locode PASSED           [ 36%]
tests/test_stack.py::test_exit_stack_unwinds_entered_writers_in_reverse_order PASSED [ 40%]
tests/test_stack.py::test_exit_stack_commits_every_manifest_on_success PASSED [ 44%]
tests/test_static.py::test_mypy_reads_exit_return_type_for_reachability[none-exit] PASSED [ 48%]
tests/test_static.py::test_mypy_reads_exit_return_type_for_reachability[bool-exit] PASSED [ 52%]
tests/test_static.py::test_mypy_types_the_with_target[class] PASSED      [ 56%]
tests/test_static.py::test_mypy_types_the_with_target[generator] PASSED  [ 60%]
tests/test_static.py::test_mypy_types_the_with_target[exit-stack] PASSED [ 64%]
tests/test_static.py::test_mypy_cannot_see_a_missing_try PASSED          [ 68%]
tests/test_writer.py::test_without_with_an_exception_leaves_the_handle_open PASSED [ 72%]
tests/test_writer.py::test_writer_closes_and_discards_on_an_exception[class] PASSED [ 76%]
tests/test_writer.py::test_writer_closes_and_discards_on_an_exception[generator] PASSED [ 80%]
tests/test_writer.py::test_writer_commits_only_on_success[class] PASSED  [ 84%]
tests/test_writer.py::test_writer_commits_only_on_success[generator] PASSED [ 88%]
tests/test_writer.py::test_writer_is_single_use PASSED                   [ 92%]
tests/test_writer.py::test_exiting_a_writer_that_was_never_entered_is_refused PASSED [ 96%]
tests/test_writer.py::test_the_generator_form_needs_try PASSED           [100%]

============================== 25 passed in 2.53s ==============================
```

```text
Success: no issues found in 7 source files
```

The suite has 16 test functions and 25 cases. The `opener` fixture closes any handle a test leaves open, so one failing test can't spill a `ResourceWarning` into another.

**Experiment one: skip the close on failure.** In a scratch copy, delete the `self._handle.close()` line from the `else` branch of `ManifestWriter.__exit__`, and run `uv run pytest -q`. Filtering to the failure lines with `uv run pytest -q | grep -E '^(FAILED|[0-9]+ (passed|failed))'` gives:

```text
FAILED tests/test_stack.py::test_exit_stack_unwinds_entered_writers_in_reverse_order
FAILED tests/test_writer.py::test_writer_closes_and_discards_on_an_exception[class]
2 failed, 23 passed in 2.69s
```

The class case fails on `assert opener.files[0].closed`, which reports `assert False`, and the stack test fails because the recorded closes are `[]` where the second and first partials were expected. The generator case passes, since it has its own copy of the logic. `uv run mypy --strict src tests` prints `Success: no issues found in 7 source files`: the type checker has no view of a missing `close()`. No warning or traceback prints after the summary line, because the fixture closes the handle. Restore the line.

**Experiment two: remove the `try` from `manifest_file`.** Replace the `try`/`except`/`else` block with `yield handle`, then `handle.close()`, then `partial.replace(path)`. One test fails:

```text
FAILED tests/test_writer.py::test_writer_closes_and_discards_on_an_exception[generator]
1 failed, 24 passed in 2.74s
```

The assertion is the same `assert opener.files[0].closed`, now against the generator. The class case still passes. mypy prints `Success: no issues found in 7 source files` again, which is what `test_mypy_cannot_see_a_missing_try` predicted. Restore the block.

## What you can do now

- Say what `with` guarantees and what it leaves to you: `ManifestWriter` closes on every path and commits only on success, shown by `test_writer_commits_only_on_success` and `test_writer_closes_and_discards_on_an_exception`.
- Write both forms: `manifest_file` is the generator version, and `test_the_generator_form_needs_try` shows the handle it leaves open without a `try`.
- Combine resources: `write_manifests` enters its writers on an `ExitStack`, and `test_exit_stack_unwinds_entered_writers_in_reverse_order` shows the unwind.
- Say what a truthy `__exit__` does: `test_a_truthy_exit_swallows_the_exception` shows the swallow, `contextlib.suppress` narrows it, and `test_mypy_reads_exit_return_type_for_reachability` shows mypy reading `-> None` against `-> bool`.
- Say how the decorator use changed: `test_a_context_manager_decorating_a_generator_spans_iteration` witnesses the 3.15 behaviour for a decorated generator function.

## For deeper coverage

The specification is [PEP 343](https://peps.python.org/pep-0343/), by Guido van Rossum and Alyssa Coghlan, and the protocol is in the Language Reference section on [with statement context managers](https://docs.python.org/3.15/reference/datamodel.html#with-statement-context-managers). The [`contextlib` documentation](https://docs.python.org/3.15/library/contextlib.html) covers `contextmanager`, `ExitStack`, `suppress` and `ContextDecorator`. [PEP 686](https://peps.python.org/pep-0686/) is the UTF-8 default, and the `contextlib` entry in [What's New in Python 3.15](https://docs.python.org/3.15/whatsnew/3.15.html) is the source for the decorator change.

Kircher and Jain's *Pattern-Oriented Software Architecture, Volume 3: Patterns for Resource Management* (2004) is the book-length treatment of resource lifetime as design. Luciano Ramalho's *Fluent Python*, second edition, covers context managers in its material on `with` blocks, and Brett Slatkin's *Effective Python*, third edition, has short rules on `with` and `contextlib`. All three are on the [bibliography page]({{ '/bibliography/' | relative_url }}).
