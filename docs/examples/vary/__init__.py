"""Override a service defined in the framework."""
from antidote import implements, interface, QualifiedBy, world


class Customer:
    name: str = "Fred"


class FrenchCustomer(Customer):
    name: str = "Jean"


@interface()
class Greeter:
    name: str
    salutation: str


@implements(Greeter).when(QualifiedBy(Customer))
class DefaultGreeter(Greeter):
    """The bundled, default greeter."""
    name: str = "Fred"
    salutation: str = "Hello"


@implements(Greeter).when(QualifiedBy(FrenchCustomer))
class FrenchGreeter(Greeter):
    """The greeter to use when we have a French customer."""
    name: str = "Marie"
    salutation = "Bonjour"


def main():
    g = world.get[Greeter].single(QualifiedBy(FrenchCustomer))
    return f"{g.salutation}, my name is {g.name}!"
