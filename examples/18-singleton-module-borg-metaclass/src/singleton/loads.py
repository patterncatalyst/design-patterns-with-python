"""A record of loads, kept apart from the modules being loaded.

The log lives here because a counter inside the module being loaded would reset whenever that
module was rebuilt, and the point of the log is to count builds.
"""

LOAD_LOG: list[str] = []


def record_load(name: str) -> None:
    """Note that the named table has just been built."""
    LOAD_LOG.append(name)
