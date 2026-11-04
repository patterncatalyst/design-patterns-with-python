import random

import pytest
from state_machines.states import InTransit
from state_machines.transit import sail_one_day, simulate_transit

_SCHEDULED = 21
_MAX_DAYS = 60
_DRAW_LIMIT = 100


class _CountingRandom(random.Random):
    """Fixture generator: every draw is the same value, and a runaway loop fails fast."""

    def __init__(self, value: float) -> None:
        super().__init__(0)
        self.value = value
        self.draws = 0

    def random(self) -> float:
        self.draws += 1
        if self.draws > _DRAW_LIMIT:
            raise AssertionError(f"more than {_DRAW_LIMIT} draws")
        return self.value


def _voyage(rng: random.Random, probability: float = 0.2) -> InTransit:
    return simulate_transit(
        InTransit("NLRTM"),
        rng=rng,
        delay_probability=probability,
        scheduled_days=_SCHEDULED,
        max_days=_MAX_DAYS,
    )


def test_a_seeded_transit_is_reproducible() -> None:
    assert _voyage(random.Random(7)).delay_days == 11
    assert _voyage(random.Random(7)).delay_days == 11
    assert _voyage(random.Random(2026)).delay_days == 3
    assert _voyage(random.Random(7)).days_sailed == _SCHEDULED


def test_a_shared_generator_gives_a_different_second_run() -> None:
    shared = random.Random(7)
    assert _voyage(shared).delay_days == 11
    assert _voyage(shared).delay_days == 5


@pytest.mark.parametrize(
    ("probability", "days_sailed", "delay_days"),
    [(0.0, _SCHEDULED, 0), (1.0, 0, _MAX_DAYS)],
    ids=["never-delayed", "always-delayed"],
)
def test_transit_delay_bounds(probability: float, days_sailed: int, delay_days: int) -> None:
    assert _voyage(random.Random(7), probability) == InTransit(
        departed_from="NLRTM", days_sailed=days_sailed, delay_days=delay_days
    )


def test_a_draw_equal_to_the_probability_is_not_a_delay() -> None:
    probability = random.Random(7).random()
    day = sail_one_day(InTransit("NLRTM"), rng=random.Random(7), delay_probability=probability)
    assert day == InTransit("NLRTM", days_sailed=1, delay_days=0)


def test_a_draw_below_the_probability_is_a_delay() -> None:
    probability = random.Random(7).random()
    day = sail_one_day(
        InTransit("NLRTM"), rng=random.Random(7), delay_probability=probability + 0.01
    )
    assert day == InTransit("NLRTM", days_sailed=0, delay_days=1)


def test_the_day_cap_bounds_the_number_of_draws() -> None:
    rng = _CountingRandom(0.0)
    voyage = simulate_transit(
        InTransit("NLRTM"), rng=rng, delay_probability=0.5, scheduled_days=_SCHEDULED, max_days=7
    )
    assert voyage == InTransit("NLRTM", days_sailed=0, delay_days=7)
    assert rng.draws == 7


def test_a_voyage_stops_drawing_once_the_schedule_is_sailed() -> None:
    rng = _CountingRandom(0.99)
    voyage = simulate_transit(
        InTransit("NLRTM"), rng=rng, delay_probability=0.5, scheduled_days=3, max_days=_MAX_DAYS
    )
    assert voyage == InTransit("NLRTM", days_sailed=3, delay_days=0)
    assert rng.draws == 3


def test_sailing_a_day_leaves_the_earlier_state_unchanged() -> None:
    start = InTransit("NLRTM", days_sailed=2, delay_days=1)
    later = sail_one_day(start, rng=random.Random(7), delay_probability=0.0)
    assert later == InTransit("NLRTM", days_sailed=3, delay_days=1)
    assert start == InTransit("NLRTM", days_sailed=2, delay_days=1)


def test_the_model_leaves_the_module_generator_alone() -> None:
    before = random.getstate()
    _voyage(random.Random(7))
    after = random.getstate()
    assert before == after
