from feature_spikes.model import answer


def test_answer() -> None:
    assert answer() == 42
