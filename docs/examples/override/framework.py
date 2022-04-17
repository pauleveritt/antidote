"""A framework which provides default implementations."""
from dataclasses import dataclass
from typing import Optional, Any

from antidote import QualifiedBy, inject, world
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
class Greeter:
    """A way to talk about all variations of a ``Greeter``."""
    salutation: str


class NoOverrides:
    """A predicate to flag the default implementation of an interface."""

    def weight(self) -> Weight:
        return Weight(float('-inf'))


@implements(Greeter).when(NoOverrides())
class DefaultAlert(Greeter):
    """The bundled ``Greeter``."""
    salutation: str = "The built-in alert"


@inject
def greeting() -> str:
    """Get a ``Greeter`` and return a greeting."""
    greeter: Greeter = world.get[Greeter].single()
    return f"{greeter.salutation}!"
