"""A probabilistic transit: each day at sea may be a delay, drawn from an injected generator."""

import random
from dataclasses import replace

from state_machines.states import InTransit


def sail_one_day(state: InTransit, *, rng: random.Random, delay_probability: float) -> InTransit:
    """Sail one day, or lose it to a delay with the given probability."""
    if rng.random() < delay_probability:
        return replace(state, delay_days=state.delay_days + 1)
    return replace(state, days_sailed=state.days_sailed + 1)


def simulate_transit(
    state: InTransit,
    *,
    rng: random.Random,
    delay_probability: float,
    scheduled_days: int,
    max_days: int,
) -> InTransit:
    """Sail until the scheduled days are sailed, giving up after max_days simulated days."""
    for _ in range(max_days):
        if state.days_sailed >= scheduled_days:
            break
        state = sail_one_day(state, rng=rng, delay_probability=delay_probability)
    return state
