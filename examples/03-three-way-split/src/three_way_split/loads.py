"""A record of module loads, kept apart from the modules being loaded."""

LOAD_LOG: list[str] = []


def record_load(name: str) -> None:
    """Note that the named module has just been built."""
    LOAD_LOG.append(name)
