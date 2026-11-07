"""Which CPython build is running, and whether its GIL is on.

The two answers can differ on a free-threaded build: the ``PYTHON_GIL`` environment
variable and the ``-X gil`` option change the runtime state of a free-threaded build.
"""

import sys
import sysconfig


def gil_disabled_build() -> bool:
    """True when this interpreter is a free-threaded build."""
    # The stub for get_config_var promises no type; bool() gives mypy a bool to return.
    return bool(sysconfig.get_config_var("Py_GIL_DISABLED"))


def gil_enabled() -> bool:
    """True when the interpreter is running with the GIL on, whichever build it is."""
    return sys._is_gil_enabled()
