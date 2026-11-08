"""Count lost updates when threads add to one shared attribute with no lock.

This is a measurement of one build on one machine, not a test: whether the race fires depends on
the build and the scheduler, so no test asserts a count. Run it with ``uv run python
bench/lost_update_probe.py --cpu-class "<a class, never a model>"`` for the default build, and with
the repository root's ``.venv-ft/bin/python`` in place of ``uv run python`` for the free-threaded
one, as the chapter's run line does from the root. The report names the Python version, the build,
whether the GIL is on and the date, and nothing that identifies the host.
"""

import argparse
import sys
import threading
from datetime import date

from gil_and_performance.build import gil_disabled_build, gil_enabled

THREADS = 4
INCREMENTS = 5_000
TRIALS = 300


class Tally:
    """A shared counter whose increment is a separate load, add and store."""

    def __init__(self) -> None:
        self.count = 0


def lost_updates() -> int:
    """Run one trial and return how many of the additions never reached the counter."""
    tally = Tally()

    def work() -> None:
        for _ in range(INCREMENTS):
            tally.count += 1

    threads = [threading.Thread(target=work) for _ in range(THREADS)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return THREADS * INCREMENTS - tally.count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu-class", default="unspecified", help="a class, never a model")
    args = parser.parse_args()

    build = "free-threading build" if gil_disabled_build() else "default build"
    version = sys.version.split()[0]
    print(f"Python {version}, {build}, GIL enabled: {gil_enabled()}")
    print(f"date: {date.today().isoformat()}, machine: {args.cpu_class}")
    print(f"switch interval: {sys.getswitchinterval()} s")
    print(f"threads: {THREADS}, additions per thread: {INCREMENTS}, trials: {TRIALS}")
    lost = [lost_updates() for _ in range(TRIALS)]
    print(f"trials with a lost update: {sum(1 for n in lost if n)} of {TRIALS}")


if __name__ == "__main__":
    main()
