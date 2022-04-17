"""A framework which provides default implementations."""
from dataclasses import dataclass
from typing import Optional, Any

from antidote import QualifiedBy
from antidote.lib.interface import Predicate
from antidote.lib.interface.interface import Weight, implements, interface


@dataclass
class Weight:
    value: float

    @classmethod
    def of_neutral(cls, predicate: Optional[Predicate[Any]]) -> Weight:
        if isinstance(predicate, QualifiedBy):
            # Custom weight
            return Weight(len(predicate.qualifiers))
        return Weight(0)

    def __lt__(self, other: Weight) -> bool:
        return self.value < other.value

    def __add__(self, other: Weight) -> Weight:
        return Weight(self.value + other.value)


@interface()
class Alert:
    name: str


class NoOverrides:
    """A predicate to flag the default implementation of an interface."""

    def weight(self) -> Weight:
        return Weight(float('-inf'))


@implements(Alert).when(NoOverrides())
class DefaultAlert(Alert):
    name = "The built-in alert"
