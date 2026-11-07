"""Which build is running.

Both tests read the build, so they assume PYTHON_GIL and -X gil are unset.
"""

import sys

from gil_and_performance.build import gil_disabled_build, gil_enabled


def test_the_build_flag_and_the_runtime_gil_state_agree() -> None:
    """Holds on either build while neither PYTHON_GIL nor -X gil overrides the GIL state."""
    assert gil_enabled() is not gil_disabled_build()


def test_sys_version_names_the_free_threading_build_only_on_that_build() -> None:
    """Holds on either build; the banner text is the one the interpreter prints."""
    assert ("free-threading build" in sys.version) is gil_disabled_build()
