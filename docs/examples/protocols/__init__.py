"""Override a service defined as a *protocol* in the framework."""
from antidote import implements, QualifiedBy

from .framework import Customer, Greeter, greeting


class FrenchCustomer(Customer):
    name: str = "Jean"


@implements(Greeter).when(QualifiedBy(FrenchCustomer))
class FrenchGreeter:
    """The greeter to use when we have a French customer."""
    name: str = "Marie"
    salutation = "Bonjour"


def main():
    # We first talk to a French customer.
    french_greeting = greeting(FrenchCustomer)

    # Now get a greeting for regular customers.
    regular_greeting = greeting(Customer)
    return french_greeting, regular_greeting
