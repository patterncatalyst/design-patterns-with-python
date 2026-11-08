---
title: "Context managers: deterministic cleanup"
order: 10
layout: tutorial
sectionid: docs
part: "python-substrate"
description: "The with statement runs &#95;&#95;exit&#95;&#95; on every path out of a block, which removes the boilerplate of Resource Acquisition; what release means, whether an exception propagates and the order across resources stay with the author."
---

## Learning objectives

By the end of this chapter you can:

- Say what `with` guarantees, and name the three decisions it leaves to the author: what release means, whether an exception propagates, and the order across several resources.
- Write a context manager as a class and as a `@contextmanager` generator, and say why the generator form needs `try`.
- Combine several resources on an `ExitStack` and predict the order they unwind in.
- Say what a truthy `__exit__` return does and how mypy's reachability analysis reads the return type.
- Say how a context manager used as a decorator changed in Python 3.15.

## Why this matters

A sailing manifest lists the consignments loaded for one port. A job writes it line by line, and halfway through the write the disk fills. Two things go wrong at once:

- The file handle stays open, because the code that would close it sits after the line that raised.
- A half-written manifest sits at the path a downstream reader polls. The reader takes it for complete, books the first forty consignments and never hears about the rest.

The first failure is a leak and the second is a lie. Both come from one gap: acquiring a resource and releasing it are two steps in different places, and an exception can fall between them. The `with` statement closes the gap. It doesn't decide what release should do, and a manifest needs more than `close()`.

{% include excalidraw.html name="10-context-managers" described="true" caption="Figure 10.1: Both ways out of a manifest write. After __enter__ opens path.partial, the body writes lines; __exit__ then replaces the partial with path on success, or unlinks it and lets the exception propagate." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-10-context-managers" markdown="1">
The accent box at the top is the `with ManifestWriter(path) as out:` line. `__enter__` opens `path.partial`, and the body writes lines to the partial file. The flow then forks. On the left the body returns, so `__exit__(None, None, None)` closes the file and replaces the partial with `path`, and the manifest is committed. On the right the body raises, so `__exit__(exc_type, exc, traceback)` closes the file, unlinks the partial and returns `None`, and the exception propagates.
</div>
</details>

The figure follows both ways out of the block: commit on success, discard and propagate on failure.

## Resource Acquisition: the force and why it survives

"Resource acquisition" is a descriptive label for a recurring design problem, not a catalogue name. The force: a resource obtained in one place must be released on every path out of the code that uses it, and what release means is a decision. Closing a handle is one answer. Committing a staged file is another. Discarding a half-finished result is a third.

[PEP 343](https://peps.python.org/pep-0343/), by Guido van Rossum and Alyssa Coghlan, added the `with` statement in Python 2.5 to take the acquire-and-release boilerplate out of call sites. The Language Reference section on [with statement context managers](https://docs.python.org/3/reference/datamodel.html#with-statement-context-managers) describes the protocol: `__enter__` runs on the way in, and `__exit__` receives the exception details, or three `None` values when the block finished normally. Michael Kircher and Prashant Jain's *Pattern-Oriented Software Architecture, Volume 3: Patterns for Resource Management* (2004) treats acquiring and releasing resources as a design topic in its own right.

This pattern survives. Nobody writes `try`/`finally` around every use any more, but three decisions remain with whoever writes the context manager:

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

`Path.replace` is how a reader comes to see the whole manifest or none of it. Without `with`, a mid-write exception leaves the handle open. Through `ManifestWriter`, the same failure closes the handle, leaves neither the partial nor the final file, and lets the `OSError` reach the caller. On success, the final path is absent inside the block and holds the manifest after it.

`__exit__` returns `None`, so the exception continues past the block. The Language Reference says that if the method "wishes to suppress the exception (i.e., prevent it from being propagated), it should return a true value. Otherwise, the exception will be processed normally upon exit from this method." Returning nothing is the decision to let the failure be seen.

Two guards cover misuse: entering the same writer twice raises `RuntimeError`, and calling `__exit__` on a writer never entered raises `was not entered`. The writer takes an `opener` callable, so tests can substitute one that records opens and closes. `open_utf8` passes `encoding="utf-8"` explicitly. Python 3.15 makes UTF-8 the default text encoding ([PEP 686](https://peps.python.org/pep-0686/), listed in [What's New in Python 3.15](https://docs.python.org/3/whatsnew/3.15.html)), and writing it out states the intent at the call site.

mypy reads the return type of `__exit__`, because it tells mypy whether the block can swallow an exception. Take a body that always raises, followed by a `return`:

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

Over a manager whose `__exit__` is annotated `-> bool`, the same function is clean, because that manager might swallow the exception and execution might reach the `return`. In all three forms below, mypy types `out` as `TextIO`.

## The generator form

`@contextmanager` turns a generator into a context manager: the code before `yield` is `__enter__`, and the code after it is `__exit__`. Generators themselves are covered in [Iterator: generators and the iterator protocol]({{ '/docs/24-iterator-generators-and-the-iterator-protocol/' | relative_url }}); here the generator is only a way to write a manager:

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

The `contextlib` documentation says: "If an unhandled exception occurs in the block, it is reraised inside the generator at the point where the yield occurred." That's why `try` isn't optional. Without it, the lines after `yield` are skipped when the block raises, so after a mid-write `OSError` the handle is still open and the partial file is still on disk. The class form can't have this bug, since `__exit__` runs on every path. mypy `--strict` accepts the generator without the `try`, so a test that raises mid-write is the only guard. Both forms run against the same cases and keep the same contract.

The annotation is `Iterator[TextIO]`, and `as out` receives the yielded handle.

## Several resources: ExitStack

One manifest per destination port means several writers, and the question is what happens when the third fails to open. Nested `with` statements don't scale to a list of unknown length, so `write_manifests` uses an `ExitStack`:

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

The [`ExitStack` documentation](https://docs.python.org/3/library/contextlib.html) says each instance "maintains a stack of registered callbacks that are called in reverse order when the instance is closed", which is the order nested `with` statements would unwind in: the last resource acquired is the first released. When the opener fails on the third call, the first and second partials were opened, the second closes first, and the directory ends up empty, because each writer's `__exit__` saw the exception and discarded its partial. The writers decide what release means, and the stack decides the order.

The contract is narrow: a failed open discards the partials of every writer entered. On success all three manifests commit and no partials remain, each writer committing on its own as the stack unwinds, so the contract says nothing about a failure at commit time.

## Swallowing an exception

A truthy `__exit__` return swallows the exception, and execution continues after the `with`. Nothing in the output says an error occurred.

Sometimes that is the intent: a cache file that may not exist yet, a cleanup of something already cleaned. `contextlib.suppress` states it narrowly. `suppress(KeyError)` swallows a `KeyError` and lets a `ValueError` from the same block propagate. The documentation for [`suppress`](https://docs.python.org/3/library/contextlib.html) says it "should be used only to cover very specific errors where silently continuing with program execution is known to be the right thing to do." Use it where the suppressed case is expected and the code after the block is valid either way. A hand-written `__exit__` that returns `True` to "keep the job going" turns every failure in the block into a success, including the ones nobody anticipated.

## A context manager as a decorator

A context manager built with `@contextmanager` can also be applied as a decorator, because it derives from `ContextDecorator`. That's the `@decorator` syntax, a function rebinding at definition time, applied to cleanup. The Decorator pattern, objects that wrap objects and compose behaviour at runtime, is a different thing; [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}) keeps the two apart.

Python 3.15 changed what this does for generator functions. The [What's New in Python 3.15](https://docs.python.org/3/whatsnew/3.15.html) entry for `contextlib` reads: "`ContextDecorator` and `AsyncContextDecorator` (and therefore `contextmanager()` and `asynccontextmanager()` used as decorators) now detect generator functions, coroutine functions, and asynchronous generator functions and keep the context manager open across iteration or await. Previously the context manager exited as soon as the generator or coroutine object was created." A decorated generator witnesses the 3.15 behaviour:

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

| | Log before iterating | Log after iterating |
| --- | --- | --- |
| Now | `[]` | `["enter", "row NLRTM", "row SGSIN", "exit"]` |
| Before the change | `['enter', 'exit']` | `['enter', 'exit', 'row NLRTM', 'row SGSIN']` |

Now the scope opens when iteration starts and closes when it ends. Before the change, it had already exited by the time the first row was produced. The source above is the authority for the "before" row, backed by a recorded run of the same snippet with `python -I` on the latest 3.14 release. On 3.15.2 it printed the first row. Code that targets only the 3.15 behaviour can rely on the decorator. For code that has to run on both, put a `with` inside the generator, which behaves the same way on both. The `async with` counterpart is in [asyncio and the patterns]({{ '/docs/38-asyncio-and-the-patterns/' | relative_url }}).

## When not to use it

- **Nothing to release.** A resource with no release step doesn't need a manager. A value computed and returned has nothing to acquire.
- **A call that cleans up after itself.** A manager wrapped around `Path.read_text`, which already closes its own file, adds a block and nothing else.
- **Swallowing to keep going.** That belongs in `suppress` with one named exception, or in an explicit `try`/`except` at the place that knows how to recover.

> **🤖 Explore with your agent**
>
> "Write `ManifestWriter` to write `<name>.partial`, close on every path, replace the final path only on success and delete the partial on failure, with `__exit__` returning `None`. In the `@contextmanager` form, wrap the `yield` in `try`/`except`/`else`. Open several writers on an `ExitStack`. Swallow only a named exception, with `contextlib.suppress`. Add a test that raises mid-write and asserts the handle is closed."
>
> If the generator form has no `try`, ask for that test run against it.

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/10-context-managers
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 25 cases pass, both writer forms against the same cases, and mypy reports `Success: no issues found in 7 source files`. An `opener` fixture closes any handle a test leaves open, so one failure can't spill a `ResourceWarning` into another. Two experiments, each in a scratch copy:

- **Skip the close on failure.** Delete `self._handle.close()` from the `else` branch of `ManifestWriter.__exit__`. Two tests fail: the class form leaves the handle open, and the `ExitStack` unwind records no closes. The generator form still passes, and mypy stays green.
- **Remove the `try` from `manifest_file`.** Replace the `try`/`except`/`else` block with `yield handle`, then `handle.close()`, then `partial.replace(path)`. The generator form now leaves the handle open on failure and one test fails. mypy stays green again.

## What you can do now

- Say what `with` guarantees and what it leaves to you: `ManifestWriter` closes on every path and commits only on success.
- Write both forms, and wrap the `yield` in `manifest_file` in `try`, because without it the handle stays open.
- Combine resources: `write_manifests` enters its writers on an `ExitStack`, which releases them in reverse.
- Say what a truthy `__exit__` does, narrow it with `contextlib.suppress`, and read how mypy treats `-> None` against `-> bool`.
- Say how the decorator use changed in Python 3.15: a decorated generator function keeps the context open across iteration.

## For deeper coverage

The specification is [PEP 343](https://peps.python.org/pep-0343/), by Guido van Rossum and Alyssa Coghlan, and the protocol is in the Language Reference section on [with statement context managers](https://docs.python.org/3/reference/datamodel.html#with-statement-context-managers). The [`contextlib` documentation](https://docs.python.org/3/library/contextlib.html) covers `contextmanager`, `ExitStack`, `suppress` and `ContextDecorator`. [PEP 686](https://peps.python.org/pep-0686/) is the UTF-8 default, and the `contextlib` entry in [What's New in Python 3.15](https://docs.python.org/3/whatsnew/3.15.html) is the source for the decorator change.

Kircher and Jain's *Pattern-Oriented Software Architecture, Volume 3: Patterns for Resource Management* (2004) is the book-length treatment of resource lifetime as design. Luciano Ramalho's *Fluent Python*, second edition, covers context managers in its material on `with` blocks, and Brett Slatkin's *Effective Python*, third edition, has short rules on `with` and `contextlib`. All three are on the [bibliography page]({{ '/bibliography/' | relative_url }}).
