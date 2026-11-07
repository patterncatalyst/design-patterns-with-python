# r20 mock census (evidence Q, step W2)

Dated 2026-11-07, at HEAD 040ead3 on release/r20, run from the repository root. The census covers every file under `examples/*/tests` and `examples/*/src` that names `mocker`, `unittest.mock`, `create_autospec`, `MagicMock` or `monkeypatch`.

## Commands and outputs

Every file that uses any of the five names, tests and sources together:

```
$ grep -rlE "mocker|unittest\.mock|create_autospec|MagicMock|monkeypatch" examples/*/tests examples/*/src | sort
examples/03-three-way-split/tests/test_disambiguate.py
examples/03-three-way-split/tests/test_dissolve.py
examples/06-isp-dip-and-di-without-a-framework/tests/test_dip.py
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_environment.py
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_static.py
examples/33-seams-in-python/tests/test_patching.py
examples/33-seams-in-python/tests/test_seams.py
examples/33-seams-in-python/tests/test_static.py
examples/34-dependency-breaking-techniques/tests/conftest.py
examples/43-appendix-c-mocking/tests/test_booking.py
examples/43-appendix-c-mocking/tests/test_calls.py
examples/43-appendix-c-mocking/tests/test_doubles.py
examples/43-appendix-c-mocking/tests/test_patching.py
examples/43-appendix-c-mocking/tests/test_spies.py
examples/43-appendix-c-mocking/tests/test_static.py
```

Sixteen files in six members (3, 6, 11, 33, 34, 43; member 42 uses none of the five names). Every one is a test file or a test conftest.

No `src` file uses a mock:

```
$ grep -rlE "mocker|unittest\.mock|create_autospec|MagicMock|monkeypatch" examples/*/src | sort
$ echo "exit $?"
exit 1
```

`grep` printed nothing and exited 1 (no match) over every `examples/*/src`.

Files that use `mocker` or `unittest.mock`:

```
$ grep -rlE "mocker|unittest\.mock" examples/*/tests | sort
examples/06-isp-dip-and-di-without-a-framework/tests/test_dip.py
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_doubles.py
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_static.py
examples/33-seams-in-python/tests/test_patching.py
examples/33-seams-in-python/tests/test_static.py
examples/43-appendix-c-mocking/tests/test_booking.py
examples/43-appendix-c-mocking/tests/test_calls.py
examples/43-appendix-c-mocking/tests/test_doubles.py
examples/43-appendix-c-mocking/tests/test_patching.py
examples/43-appendix-c-mocking/tests/test_spies.py
examples/43-appendix-c-mocking/tests/test_static.py
```

Files that use `monkeypatch`:

```
$ grep -rlE "monkeypatch" examples/*/tests | sort
examples/03-three-way-split/tests/test_disambiguate.py
examples/03-three-way-split/tests/test_dissolve.py
examples/11-testing-with-pytest-pytest-mock-and-mypy/tests/test_environment.py
examples/33-seams-in-python/tests/test_patching.py
examples/33-seams-in-python/tests/test_seams.py
examples/33-seams-in-python/tests/test_static.py
examples/34-dependency-breaking-techniques/tests/conftest.py
examples/43-appendix-c-mocking/tests/test_patching.py
```

Counts: 16 files in all; 11 with `mocker` or `unittest.mock`; 8 with `monkeypatch`; 3 with both (`33 test_patching.py`, `33 test_static.py`, `43 test_patching.py`); 0 under `src`.

## Mock APIs per file

Read from the files (each line below was checked against `grep -nE "mocker|Mock|patch|assert_|side_effect|return_value|spec"` on the file). "Snippet" means the API appears only inside a string that a test hands to mypy; it is not executed.

### Member 03 (three-way split)

- `03 tests/test_dissolve.py`: `monkeypatch.setattr(module, "NAME", value)` (1 use).
- `03 tests/test_disambiguate.py`: `monkeypatch.setattr(module, "NAME", value)` (1 use).

### Member 06 (ISP, DIP and DI without a framework)

- `06 tests/test_dip.py`: `mocker.create_autospec(Protocol, instance=True)` (3 uses); `assert_called_once_with`.

### Member 11 (testing with pytest, pytest-mock and mypy)

- `11 tests/test_doubles.py`: `mocker.create_autospec(..., instance=True)` (5); `mocker.Mock()` and `mocker.Mock(spec=...)` (2); `.return_value`; `.side_effect`; `assert_called_once_with`; `assert_not_called`.
- `11 tests/test_environment.py`: `monkeypatch.context()` with `patch.setenv` and `patch.delenv`.
- `11 tests/test_static.py` (snippets): `Mock()`, `Mock(spec=...)`, `MagicMock(spec=...)`, `create_autospec(..., instance=True)` imported from `unittest.mock`.

### Member 33 (seams in Python)

- `33 tests/test_patching.py`: `monkeypatch.setattr` by dotted string and by object (10); `monkeypatch.context()`; `mocker.patch("...")`, `mocker.patch(..., create=True)`, `mocker.patch(..., autospec=...)` (3); `unittest.mock.patch` as a context manager (1); `raising=False`.
- `33 tests/test_seams.py`: `monkeypatch.setattr` (6); `pytest.MonkeyPatch.context()` at module level.
- `33 tests/test_static.py`: `monkeypatch.setattr` (4); snippets of `unittest.mock.patch` as a context manager (with and without `new=`) and as a decorator; `MagicMock`; `.return_value`; `AsyncMock` in the expected `reveal_type` string.

### Member 34 (dependency-breaking techniques)

- `34 tests/conftest.py`: `monkeypatch.setattr` (2), the one namespace patch of the member, taken with `request.getfixturevalue("monkeypatch")`.

### Member 43 (Appendix C, mocking reference)

- `43 tests/test_doubles.py`: `mocker.Mock()` with `spec=`, `spec_set=`, `unsafe=True`, `wraps=`; `mocker.MagicMock()`; `mocker.AsyncMock()`; `mocker.seal`; `.return_value`; `.call_count`; `assert_called_once_with`; `assert_awaited_once_with`.
- `43 tests/test_calls.py`: `mocker.create_autospec(..., instance=True)` (6); `mocker.Mock()` as a manager; `attach_mock` (2); `mocker.stub()`; `.side_effect` (iterable and callable); `.mock_calls`; `.call_args`; `.call_args_list`; `.call_count`; `unittest.mock.call` and `call.<child>` chains; `mock.ANY`; `assert_has_calls` (with and without `any_order`); `assert_any_call`; `reset_mock`.
- `43 tests/test_booking.py`: `mocker.create_autospec(..., instance=True)` (4); `mocker.stub()` (3); `.return_value`; `.side_effect`; `assert_not_called`.
- `43 tests/test_patching.py`: `mocker.patch.object(..., autospec=True)` (4); `mocker.patch.dict`; `mocker.stop`; `mocker.stopall` (2); `assert_called_once_with`; `monkeypatch.setenv` and `monkeypatch.delenv`.
- `43 tests/test_spies.py`: `mocker.spy` (3) with `.spy_return` and `.spy_exception`; `mocker.stub()` (2); `mocker.create_autospec` (async function and class); `mocker.patch.object`; `mocker.Mock`; `mocker.resetall`; `MagicMock`; `.call_count`; `assert_called_once_with`; `assert_awaited_once_with`.
- `43 tests/test_static.py` (snippets): `mocker.patch`, `mocker.patch.object`, `mocker.patch.dict`, `mocker.spy`, `mocker.stub`, `mocker.Mock`; `unittest.mock.patch`, `MagicMock`, `NonCallableMagicMock`, `AsyncMock`; `pytest_mock.plugin.SpyType` in the expected `reveal_type` strings.

## Reading

- Tests mock in three chapters' members (6, 11, 33) plus the 34 conftest patch, the 03 `monkeypatch` pair and the new member 43. No file under `src` imports or names a mock, a patch or `monkeypatch`.
- Older members use `create_autospec`, `Mock(spec=)`, `mocker.patch` and `monkeypatch.setattr`. Member 43 is the only one that uses `mocker.spy`, `mocker.stub`, `mocker.seal`, `mocker.patch.dict`, `mocker.patch.object`, `mocker.stop`, `mocker.stopall`, `mocker.resetall`, `AsyncMock`, `attach_mock` and `assert_has_calls`.
