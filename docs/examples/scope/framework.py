"""A framework which provides default implementations."""
from dataclasses import dataclass
from typing import Protocol, Optional

from antidote import QualifiedBy, world, service, Inject, inject, factory
from antidote.lib.interface.interface import implements, interface

VISIT_SCOPE = world.scopes.new(name="visit")


class Customer:
    name: str = "Fred"


@dataclass(frozen=True)
class Visit:
    customer: Optional[Customer] = None


@factory(scope=VISIT_SCOPE)
class VisitHandler:
    def __init__(self):
        self.__visit = None

    def __call__(self) -> Visit:
        assert self.__visit is not None
        return self.__visit

    def set_customer(self, customer: Customer) -> None:
        self.__visit = Visit(customer=customer)
        world.scopes.reset(VISIT_SCOPE)


@interface()
class Greeter(Protocol):
    """A way to talk about all variations of a ``Greeter``."""
    name: str
    salutation: str


@implements(Greeter).when(QualifiedBy(Customer))
@dataclass
class DefaultGreeter:
    """The bundled ``Greeter``."""
    name: str = "Fred"
    salutation: str = "Hello"


@inject
def greeting(visit: Visit = inject.me(source=VisitHandler)) -> str:
    """Get a ``Greeter`` for a ``Customer`` and return a greeting."""
    customer_type = visit.customer.__class__
    greeter = world.get[Greeter].single(QualifiedBy(customer_type))
    return f"{greeter.salutation}, my name is {greeter.name}!"


@inject
def handle_visit(
    customer: Customer,
    visit_handler: Inject[VisitHandler]
) -> str:
    """Reset scope to use current customer and return greeting."""
    visit_handler.set_customer(customer=customer)
    return greeting()
