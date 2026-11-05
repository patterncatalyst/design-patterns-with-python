"""The @decorator syntax: a function name rebound at definition time."""

from collections.abc import Callable
from functools import wraps

from decorator_proxy.domain import CarrierQuote, CarrierTimeoutError, Consignment
from decorator_proxy.proxy import CarrierGateway


def retry[**P, R](
    *, attempts: int, on: tuple[type[BaseException], ...]
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Call the function again after any exception in ``on``, up to ``attempts`` calls in all."""
    if attempts < 1:
        raise ValueError(f"attempts must be at least 1, got {attempts}")

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for _ in range(attempts - 1):
                try:
                    return func(*args, **kwargs)
                except on:
                    continue
            return func(*args, **kwargs)

        return wrapper

    return decorate


def audited[**P, R](sink: Callable[[str], None]) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Report each call of the decorated function to ``sink``."""

    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            sink(func.__name__)
            return func(*args, **kwargs)

        return wrapper

    return decorate


@retry(attempts=3, on=(CarrierTimeoutError,))
def quote_carrier(gateway: CarrierGateway, consignment: Consignment) -> CarrierQuote:
    """Ask a carrier for a price, trying again after a timeout."""
    return gateway.quote(consignment)
