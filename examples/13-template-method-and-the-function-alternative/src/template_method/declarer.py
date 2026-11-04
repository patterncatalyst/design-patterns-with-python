"""The class form of Template Method: a family of destinations that share state and code."""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from decimal import Decimal
from typing import ClassVar, final, override

from template_method.domain import (
    Commodity,
    Consignment,
    CustomsDeclaration,
    DeclarationLine,
    Money,
)
from template_method.hooks import CustomsHooks, declare_customs, lookup_tariff_code, schedule_duty


class CustomsDeclarer(ABC):
    """Destinations that share a classification and a schedule. The template is final."""

    country: ClassVar[str]

    def __init__(
        self, *, classification: Mapping[str, str], schedule: Mapping[str, Decimal]
    ) -> None:
        self.classification = classification
        self.schedule = schedule

    def classify(self, commodity: Commodity) -> str:
        return lookup_tariff_code(self.classification, commodity, self.country)

    def duty(self, lines: tuple[DeclarationLine, ...]) -> Money:
        return schedule_duty(lines, schedule=self.schedule)

    @abstractmethod
    def extra_documents(self, consignment: Consignment) -> tuple[str, ...]: ...

    @final
    def declare(self, consignment: Consignment) -> CustomsDeclaration:
        hooks = CustomsHooks(
            country=self.country,
            classify=self.classify,
            duty=self.duty,
            extra_documents=self.extra_documents,
        )
        return declare_customs(consignment, hooks=hooks)


class NetherlandsDeclarer(CustomsDeclarer):
    country = "NL"

    @override
    def extra_documents(self, consignment: Consignment) -> tuple[str, ...]:
        return ("EUR.1 movement certificate",)


class GermanyDeclarer(CustomsDeclarer):
    country = "DE"

    @override
    def extra_documents(self, consignment: Consignment) -> tuple[str, ...]:
        return ("Intrastat declaration",)
