---
title: "Decorators done right"
order: 26
layout: tutorial
sectionid: docs
part: "idiomatic-python"
description: "The @ syntax is given, but getting a decorator right isn't: what wraps copies, what ParamSpec keeps for mypy, bare use of a factory, stacking order and class decorators."
---

## Learning objectives

By the end of this chapter you can:

- Keep a decorated function's name, docstring and signature for runtime tools with `functools.wraps`, and say what it copies and where it misleads.
- Type a decorator for mypy with `ParamSpec`, including one that supplies an argument with `Concatenate`.
- Write a decorator factory that refuses bare use when the module loads.
- Build a cache with an injected clock and choose where a timer sits in the stack.
- Place a class decorator above `@dataclass(slots=True)`, and decorate a method without keeping its instances alive.

## Why this matters

A booking portal renders bills of lading, caches each rendering for five minutes and times the work. Each of those is a decorator over one function, `render_bill`. The `@` that applies them is the language's part: it rebinds a name when the function is defined. What stays design is the discipline around it, so the bucket is survives. The map in [The three-way split: dissolve, survive, disambiguate]({{ '/docs/03-the-three-way-split/' | relative_url }}) files the shared name under needs disambiguating. The obvious versions fail three ways:

- A renderer reports itself as `wrapper` with no docstring, so a log line or a help page names a function nobody wrote.
- A cache factory takes its window positionally and someone writes `@cached_for` with no call. Nothing fails, and calling the result returns a function where text was expected.
- A class decorator sits beneath `@dataclass(slots=True)`, and the registry holds a class the code never uses.

{% include excalidraw.html name="26-decorators-done-right" described="true" caption="Figure 26.1: The order of a stack decides whether a timer sees a cache hit. functools.wraps keeps a renderer's identity for runtime tools, ParamSpec keeps its signature for mypy, and a class decorator belongs above a slotted dataclass." %}

<details class="figure-description" markdown="1">
<summary>Describe the figure</summary>
<div id="desc-26-decorators-done-right" markdown="1">
From the top down, a box reading "a render function", "the function both stacks wrap", has an arrow to each stack. On the left `timed_render` is outer and `cached_for` inner, with the note "timer outside: every call timed" beneath. On the right `cached_for` is outer and `timed_render` inner, with "timer inside: only misses timed" beneath. Lower down, `functools.wraps` ("copies name, doc, dict; adds __wrapped__") leads to `inspect.signature` ("follows __wrapped__"), and `ParamSpec` ("keeps the signature") leads to `mypy` ("sees the original parameters"). Between them a dashed, muted box reads "a decorator that supplies an argument: the signature misleads; use partial". At the bottom `document_kind` ("above: registers the class the name holds") leads to `dataclass(slots=True)` ("returns a new class").
</div>
</details>

The figure sets the two stacking orders above the two tools that keep a wrapper looking like the original, one for runtime tools and one for mypy.

## What wraps copies

A decorator replaces a function with another one, and everything that reads the function afterwards reads the replacement: a log line, a help page, a debugger, a signature check. `functools.wraps` makes the replacement look like the original. The rebinding itself is covered in [Decorator the pattern vs @decorator the syntax, and Proxy]({{ '/docs/20-decorator-pattern-vs-decorator-syntax-and-proxy/' | relative_url }}).

```python
def timed_render[**P, R](
    sink: TimingSink, *, clock: Clock = time.perf_counter
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Report the function's name and the elapsed clock time to ``sink`` after every call."""

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            started = clock()
            try:
                return func(*args, **kwargs)
            finally:
                sink(func.__name__, clock() - started)

        return wrapper

    return decorate
```

`wraps` applies `functools.update_wrapper`, which the [functools documentation](https://docs.python.org/3/library/functools.html) sums up as "Update a wrapper function to look like the wrapped function." The same page says the function "automatically adds a __wrapped__ attribute to the wrapper that refers to the function being wrapped".

A copy of the timer without `wraps` renders the same text. Only what a tool reads off it differs:

| Attribute | With `wraps` | Without |
| --- | --- | --- |
| `__name__` | `render_bill` | `wrapper` |
| `__qualname__` | `render_bill` | ends in `<locals>.wrapper` |
| `__doc__` | the original | `None` |
| `__dict__` | copied from the function | empty |
| `__wrapped__` | the function one level down | missing |
| `inspect.signature` | `(bill: decorators_done_right.domain.BillOfLading, /, *, width: int = 72) -> str` | `(*args: P.args, **kwargs: P.kwargs) -> R` |

`__wrapped__` points one level down: with a timer over a cache over `render_bill`, the timer's `__wrapped__` is the cache wrapper, and the cache wrapper's is `render_bill`. The [inspect documentation](https://docs.python.org/3/library/inspect.html) describes `inspect.unwrap` as one that "follows the chain of __wrapped__ attributes returning the last object in the chain", and `inspect.signature` follows the same chain.

One attribute changed. PEP 749, by Jelle Zijlstra, says: "functools.update_wrapper() (and therefore functools.wraps()) will copy only the __annotate__ attribute from the wrapped object to the wrapper." That holds since Python 3.14, when annotations became evaluated on demand. On 3.15.2 `functools.WRAPPER_ASSIGNMENTS` contains `__annotate__` and not `__annotations__`, and the wrapper's `__annotations__` still equals the original's. The functools page for 3.15.2 still lists `__annotations__` among the attributes it assigns, so the constant is the one to read.

## What mypy reads

mypy doesn't read `__wrapped__`. It reads the wrapper's declared type, and `ParamSpec` carries the wrapped function's parameters through that type. [PEP 612](https://peps.python.org/pep-0612/), by Mark Mendoza, says: "This PEP proposes typing.ParamSpec and typing.Concatenate to support expressing these kinds of relationships." So `wraps` serves runtime tools, `ParamSpec` serves mypy, and a wrapper can have either without the other:

| Timer | What mypy sees |
| --- | --- |
| `ParamSpec`, no `wraps` | `render_bill(bill, /, *, width: int = 72)`; `width="30"` is `[arg-type]` |
| no annotations | `[untyped-decorator]`, `Untyped decorator makes function "render_bill" untyped`, plus `[no-untyped-def]` |

`Concatenate` is for a decorator that supplies an argument. The [typing documentation](https://docs.python.org/3/library/typing.html) says it "can be used in conjunction with Callable and ParamSpec to annotate a higher-order callable which adds, removes, or transforms parameters of another callable". A decorator over `render(width, bill, /)` that supplies `width` leaves mypy seeing a function of the bill alone, and a call that repeats the width is `[call-arg]` and `[arg-type]`.

Runtime tools disagree, and `wraps` is the cause. A decorator that fixes the clock argument of `issued_at(clock, number)` and uses `wraps` gives `stamp("BL-1")` returning `BL-1 issued at 1000`, yet `inspect.signature(stamp)` lists `clock` and `number`, and `signature.bind("BL-1")` raises `TypeError` with "missing a required argument". `functools.partial(issued_at, clock)` reports `number` alone and its `bind` accepts the call. `wraps` assumes the wrapper takes the wrapped function's arguments; when it supplies one, use `partial`.

## Factories that refuse to be used bare

A decorator with parameters is a function that returns a decorator, so `@cached_for(seconds=300)` has a call after the name. The [compound statements reference](https://docs.python.org/3/reference/compound_stmts.html) says "Decorator expressions are evaluated when the function is defined, in the scope that contains the function definition." The call runs at definition, and so does any mistake in it. Here's a factory that takes its window positionally:

```python
def _cached_for_positional[**P, R](
    seconds: float,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """The comparison: the window is a positional argument, so a bare ``@`` use is not refused."""

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(*args, **kwargs)

        return wrapper

    return decorate
```

Used bare, as `@positional_factory` with no call, it fails without an error. The name is bound to the inner `decorate`, and calling it with a bill returns the wrapper. mypy refuses the bare use with `[arg-type]`, but only where mypy runs.

| Factory | Bare `@` at run time | mypy |
| --- | --- | --- |
| positional `seconds` | binds the name to `decorate`; no error | `[arg-type]` |
| keyword-only `*, seconds` | `TypeError`, "takes 0 positional arguments", when the module loads | `[call-arg]` and `[arg-type]` |

The `*` before `seconds` is what makes the refusal. Without it the bare use still fails at the `def`, but only because the window check compares a function with `0`.

## A cache with a clock, and the order of the stack

A cache over rendered text has to expire, and a test can't wait for it to. `cached_for` takes the clock as an argument, so time advances by hand. The `[**P, R]` after the name is the type-parameter syntax of PEP 695, by Eric Traut, with `ParamSpec` from PEP 612.

```python
def cached_for[**P, R](
    *, seconds: float, clock: Clock = time.monotonic
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Serve a result again for ``seconds`` of clock time, one entry per distinct arguments.

    Single-threaded, and every argument must be hashable.
    """
    if seconds <= 0:
        raise ValueError(f"seconds must be positive, got {seconds}")

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        entries: dict[Hashable, tuple[float, R]] = {}

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = (args, frozenset(kwargs.items()))
            now = clock()
            entry = entries.get(key)
            if entry is not None and now - entry[0] < seconds:
                return entry[1]
            result = func(*args, **kwargs)
            entries[key] = (now, result)
            return result

        return wrapper

    return decorate
```

- Two calls inside the window render once.
- The entry is stamped when the call starts, so the render's own clock time counts against the window. A call exactly one window later renders again.
- Each distinct argument has its own entry, including a keyword argument such as `width=30`.
- A list passed positionally raises `TypeError`, with the message "cannot use 'tuple' as a dict key (unhashable type: 'list')".
- A window of zero or less is a `ValueError`.
- The cache is single-threaded, as its docstring says.

`timed_render` reports the elapsed clock time whether the render returns or raises.

Stacking decides what the timer sees. The compound statements reference says "Multiple decorators are applied in nested fashion", and its example reads `@f1(arg)` over `@f2` as `f1(arg)(f2(func))`: the decorator nearest the `def` applies first. The two orders, written as calls:

<!-- fmt:off -->
```python
    stacked = timer(cache(render)) if timer_outside else cache(timer(render))
```
<!-- fmt:on -->

Called twice with the same bill, both orders render once:

| Order | Sink receives | Measures |
| --- | --- | --- |
| timer outside | `("render", 2.0)`, then `("render", 0.0)` | what the caller waited, hits included |
| timer inside | `("render", 2.0)` only | the renderer |

A dashboard of renderer cost wants the timer inside, and one of response time wants it outside.

## Class decorators

A registry of document classes shouldn't depend on someone remembering to call `register(BillOfLading)`. `document_kind` is a class decorator that registers at definition:

```python
def document_kind[C: type](
    kind: DocumentKind, *, registry: dict[DocumentKind, type] = DOCUMENT_TYPES
) -> Callable[[C], C]:
    """Register the decorated class for ``kind`` and return it unchanged.

    Put it above ``@dataclass(slots=True)``: that decorator returns a new class, and a
    decorator beneath it would register the class that is thrown away.
    """

    def register(cls: C) -> C:
        if kind in registry:
            raise DocumentKindError(
                f"{kind.name} is already registered to {registry[kind].__qualname__}"
            )
        registry[kind] = cls
        return cls

    return register


@document_kind(DocumentKind.BILL_OF_LADING)
@dataclass(frozen=True, slots=True)
class BillOfLading:
    number: str
    consignment_id: ConsignmentId
    port_of_loading: str
    port_of_discharge: str
```

Importing the module fills `DOCUMENT_TYPES` with `BillOfLading` and `Manifest`, and a second class for the same kind raises `DocumentKindError`. mypy doesn't apply a class decorator's return type: a decorated class keeps its own type whatever the decorator declares, so `BillOfLading.number` is a `str` even under a decorator declared to return `int`. Class decorators come from [PEP 3129](https://peps.python.org/pep-3129/), by Collin Winter, which extended the `@` form to classes.

The order against `@dataclass(slots=True)` matters. The [dataclasses documentation](https://docs.python.org/3/library/dataclasses.html) says of `slots`: "If true (the default is False), __slots__ attribute will be generated and new class will be returned instead of the original one." With `document_kind` beneath it, the registry holds a class without `__slots__` and the name holds the slotted one. Put above, as on `BillOfLading` and `Manifest`, it registers the class the name ends up holding.

A class decorator that doesn't return the class binds the name to `None`, and mypy reports `[return]`, `Missing return statement`. Registering classes by other means is covered in [Metaclasses, __init_subclass__, and registries]({{ '/docs/29-metaclasses-init-subclass-and-registries/' | relative_url }}).

## Decorating methods

A function wrapper works on a method unchanged. The [descriptor guide](https://docs.python.org/3/howto/descriptor.html) says "To support automatic creation of methods, functions include the __get__() method for binding methods during attribute access." The wrapper `timed_render` returns is a function, so `Renderer().render("BL-1")` binds `self` and the timer records the call. A class-based wrapper with `__call__` and no `__get__` has nothing to bind with: the instance is never passed, `"BL-1"` fills `self`, and the call fails with "missing 1 required positional argument". Writing `__get__` is covered in [Descriptors and properties]({{ '/docs/27-descriptors-and-properties/' | relative_url }}).

`functools.cache` on a method has a different cost. The functools page says "If a method is cached, the self instance argument is included in the cache." The [programming FAQ](https://docs.python.org/3/faq/programming.html) gives the consequence: "The disadvantage is that instances are kept alive until they age out of the cache or until the cache is cleared". A `weakref` to the instance still resolves after `del` and `gc.collect()`, and stops resolving after `Renderer.render.cache_clear()`. Ruff's [B019 rule](https://docs.astral.sh/ruff/rules/cached-instance-method/) flags it: "Using the functools.lru_cache and functools.cache decorators on methods can lead to memory leaks, as the global cache will retain a reference to the instance, preventing it from being garbage collected."

## When not to use it

- **Per-object behaviour.** When behaviour has to vary per object while the program runs, a decorator can't help, because it fixes the wrapping when the function is defined; wrapper objects that share an interface, composed at run time, can.
- **Supplying an argument.** Use `functools.partial`, which reports the signature that's left.
- **Fresh or unhashable data.** A cache over data that must be fresh serves the wrong answer for a window, and one over unhashable arguments raises.
- **An unread registry.** A registry that nobody reads is a dictionary to keep in step.

<blockquote class="ai-sidebar" markdown="1">
**Specifying a decorator.** "A caching decorator" doesn't say how the wrapper keeps its identity, how the window is passed or where the timer sits, so the reply decides each one for you. State them in the prompt:

> Write `cached_for` as a PEP 695 `[**P, R]` factory with keyword-only `seconds` and an injected `clock`, its wrapper decorated with `functools.wraps(func)` and typed `Callable[P, R]`. Put `timed_render` inside the cache so only misses are timed. Where a decorator would supply an argument, use `functools.partial`. Put `document_kind` above `@dataclass(slots=True)`, and never put `functools.cache` on a method.

If the reply drops `wraps` or the `*`, ask for the test that fails.
</blockquote>

## Build, run, observe

From the repository root, once, `uv sync --locked --all-packages`. Then:

```bash
cd examples/26-decorators-done-right
uv run pytest -v --no-header
uv run mypy --strict src tests
```

All 40 cases pass and mypy is clean. For how the mypy checks run from pytest, see [Proving it works: pytest, pytest-mock, and mypy]({{ '/docs/11-testing-with-pytest-pytest-mock-and-mypy/' | relative_url }}). Two experiments:

- **Remove `wraps` from the timer.** In a scratch copy, delete the `@wraps(func)` line from `timed_render`'s wrapper. Five metadata tests fail: the name, the signature, the copied dictionary, `__wrapped__` and the annotations. The rendered text still matches, and mypy stays green, because `ParamSpec` still carries the signature.
- **Make `seconds` positional.** In a scratch copy, delete the `*,` from `cached_for`'s parameters. Two tests fail: bare `@cached_for` now fails with "'<=' not supported between instances of 'function' and 'int'" instead of the refusal, and mypy reports only `[arg-type]`. mypy fails too, with `[unused-ignore]` on the half-unused `# type: ignore[call-arg, arg-type]`.

## What you can do now

- Keep identity and signature with `functools.wraps` on `timed_render`, and know the five attributes a bare wrapper loses.
- Type a decorator with `ParamSpec`, use `Concatenate` for one that supplies an argument, and reach for `functools.partial` when `wraps` would mislead `inspect.signature`.
- Refuse bare use with the keyword-only `cached_for`, which fails when the module loads.
- Build `cached_for` on an injected clock and place the timer inside or outside it by what you measure.
- Put `document_kind` above `@dataclass(slots=True)`, and keep `functools.cache` off methods.

## For deeper coverage

[PEP 318](https://peps.python.org/pep-0318/), by Kevin D. Smith, Jim J. Jewett, Skip Montanaro and Anthony Baxter, introduced decorators for functions and methods, and [PEP 3129](https://peps.python.org/pep-3129/) extended them to classes. [PEP 612](https://peps.python.org/pep-0612/) specifies `ParamSpec` and `Concatenate`, [PEP 695](https://peps.python.org/pep-0695/) the type-parameter syntax the factories use, and [PEP 749](https://peps.python.org/pep-0749/) the `__annotate__` change. The [functools](https://docs.python.org/3/library/functools.html), [inspect](https://docs.python.org/3/library/inspect.html), [typing](https://docs.python.org/3/library/typing.html) and [dataclasses](https://docs.python.org/3/library/dataclasses.html) documentation cover the functions used here, the [compound statements reference](https://docs.python.org/3/reference/compound_stmts.html) covers decorator evaluation, and the [descriptor guide](https://docs.python.org/3/howto/descriptor.html) covers why functions bind. The [programming FAQ](https://docs.python.org/3/faq/programming.html) and ruff's [B019 page](https://docs.astral.sh/ruff/rules/cached-instance-method/) cover caching methods. The [bibliography page]({{ '/bibliography/' | relative_url }}) lists the books.
