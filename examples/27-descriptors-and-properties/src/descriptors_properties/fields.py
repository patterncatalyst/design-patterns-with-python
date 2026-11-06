"""The validating descriptor shared by every positive field."""

from decimal import Decimal
from typing import Never, overload


class Positive:
    """A managed attribute that accepts only finite, positive ``Decimal`` values.

    ``__set_name__`` gives each field its own public name and its own storage name. Class access
    raises ``AttributeError``, so a dataclass field built on this descriptor has no default. Storage
    goes through ``vars()``, because ``setattr`` on a frozen dataclass raises
    ``FrozenInstanceError``.
    """

    public_name: str
    private_name: str

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name
        self.private_name = f"_{name}"

    @overload
    def __get__(self, instance: None, owner: type) -> Never: ...

    @overload
    def __get__(self, instance: object, owner: type) -> Decimal: ...

    def __get__(self, instance: object | None, owner: type) -> Decimal:
        if instance is None:
            raise AttributeError(self.public_name)
        value: Decimal = vars(instance)[self.private_name]
        return value

    def __set__(self, instance: object, value: Decimal) -> None:
        if not value.is_finite() or value <= 0:
            raise ValueError(f"{self.public_name} must be positive, got {value}")
        vars(instance)[self.private_name] = value
