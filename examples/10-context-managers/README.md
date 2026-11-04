# Context managers

A sailing manifest written to a `.partial` file and committed only when the write succeeds, in
three forms: a class with `__enter__` and `__exit__`, a `@contextmanager` generator and an
`ExitStack` over several writers. Each test witnesses a claim about what `with` guarantees and
what the author still decides. The chapter's thesis is that Resource Acquisition survives: `with`
removes the boilerplate, and what release means stays a design decision.

## What it witnesses

Release on every path.

- Without `with`, an exception mid-write leaves the handle open and nothing closes it.
- `ManifestWriter` and `manifest_file` close the handle on success and on failure, commit by
  `Path.replace` only on success and discard the partial file on failure.
- `ManifestWriter` is single-use, and exiting one that was never entered is refused.
- The generator form needs `try`: without it the code after `yield` never runs on an exception, and
  mypy reports nothing.

Several resources.

- `write_manifests` enters one writer per manifest on an `ExitStack`. When the third open fails,
  the two entered writers exit in reverse order and no final or partial file remains.

What `__exit__` returns.

- A truthy return swallows the exception. `contextlib.suppress` swallows only the named one.
- mypy reads the return type: with `-> None`, code after a `with` whose body always raises is
  unreachable under `--warn-unreachable`; with `-> bool` it is reachable.

Python 3.15.

- A context manager used as a decorator on a generator function stays entered across iteration.
  Before 3.15 it exited as soon as the generator object was created. The test asserts the 3.15
  behaviour only.

## Layout

- `src/context_managers/manifest.py`: `ConsignmentId`, `Manifest`, `Opener`, `open_utf8`,
  `render_line`, `ManifestWriter`, `manifest_file`, `write_manifests`.
- `tests/conftest.py`: `RecordingOpener`, which wraps a real UTF-8 file and records opens and
  closes in order, and can fail on the Nth open.

## Run it

From the repository root, once:

```bash
uv sync --locked --all-packages
```

Then from this directory:

```bash
uv run pytest
uv run mypy --strict src tests
```

Tests write only under pytest's `tmp_path`.

## What the tests verify

`tests/test_writer.py`

- `test_without_with_an_exception_leaves_the_handle_open`: the handle is still open after the error.
- `test_writer_closes_and_discards_on_an_exception`: class and generator both close, remove the partial file and propagate.
- `test_writer_commits_only_on_success`: the final file is absent inside the block and present after.
- `test_writer_is_single_use`: a second `with` on the same writer raises `RuntimeError`.
- `test_exiting_a_writer_that_was_never_entered_is_refused`: `__exit__` without `__enter__` raises.
- `test_the_generator_form_needs_try`: without `try` the handle stays open and the partial file remains.

`tests/test_stack.py`

- `test_exit_stack_unwinds_entered_writers_in_reverse_order`: closes are second writer, then first writer.
- `test_exit_stack_commits_every_manifest_on_success`: three manifests are committed and no partial remains.

`tests/test_semantics.py`

- `test_a_truthy_exit_swallows_the_exception`: the code after the block runs.
- `test_suppress_swallows_only_the_named_exception`: `KeyError` is swallowed, `ValueError` propagates.
- `test_a_context_manager_decorating_a_generator_spans_iteration`: enter, rows, then exit.
- `test_manifest_rejects_a_port_that_is_not_a_locode`: five malformed ports raise `ValueError`.
- `test_manifest_accepts_a_locode`: a well-formed port is kept.

`tests/test_static.py`

- `test_mypy_reads_exit_return_type_for_reachability`: `[unreachable]` for `-> None`, clean for `-> bool`.
- `test_mypy_types_the_with_target`: `assert_type(out, TextIO)` for class, generator and `ExitStack`.
- `test_mypy_cannot_see_a_missing_try`: the leaky generator type-checks cleanly.

Classes and functions named with a leading underscore in the test modules are negative fixtures
and are not part of the model code.
