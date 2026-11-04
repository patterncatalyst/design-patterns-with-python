import os
from datetime import timedelta

import pytest
from testing_baseline.engine import VALIDITY_VARIABLE, validity_from_env


def test_validity_reads_the_environment_and_the_context_restores_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    before = os.environ.get(VALIDITY_VARIABLE)

    with monkeypatch.context() as patch:
        patch.setenv(VALIDITY_VARIABLE, "45")
        assert validity_from_env() == timedelta(minutes=45)
        patch.delenv(VALIDITY_VARIABLE)
        assert validity_from_env() == timedelta(minutes=30)
        patch.setenv(VALIDITY_VARIABLE, "7")

    assert os.environ.get(VALIDITY_VARIABLE) == before


def test_validity_defaults_to_thirty_minutes_when_unset() -> None:
    assert validity_from_env({}) == timedelta(minutes=30)


def test_validity_accepts_a_positive_int() -> None:
    assert validity_from_env({VALIDITY_VARIABLE: "90"}) == timedelta(minutes=90)


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("0", id="zero"),
        pytest.param("-5", id="negative"),
        pytest.param("soon", id="text"),
    ],
)
def test_validity_rejects_a_value_that_is_not_a_positive_int(value: str) -> None:
    with pytest.raises(ValueError, match=VALIDITY_VARIABLE):
        validity_from_env({VALIDITY_VARIABLE: value})
