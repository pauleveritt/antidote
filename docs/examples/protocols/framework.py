"""A framework which provides default implementations."""
from typing import Type, Protocol

from antidote import QualifiedBy, world
from antidote.lib.interface.interface import implements, interface


class Customer:
    name: str = "Fred"


@interface()
class Greeter(Protocol):
    """A way to talk about all variations of a ``Greeter``."""
    name: str
    salutation: str


@implements(Greeter).when(QualifiedBy(Customer))
class DefaultGreeter:
    """The bundled ``Greeter``."""
    name: str = "Fred"
    salutation: str = "Hello"


def greeting(customer_type: Type[Customer]) -> str:
    """Get a ``Greeter`` and return a greeting."""
    greeter = world.get[Greeter].single(QualifiedBy(customer_type))
    return f"{greeter.salutation}, my name is {greeter.name}!"
