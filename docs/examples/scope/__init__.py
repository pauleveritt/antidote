"""Represent each customer visit inside the ``world`."""

from antidote import implements, QualifiedBy

from .framework import Customer, Greeter, greeting, handle_visit


class FrenchCustomer(Customer):
    name: str = "Jean"


@implements(Greeter).when(QualifiedBy(FrenchCustomer))
class FrenchGreeter:
    """The greeter to use when we have a French customer."""
    name: str = "Marie"
    salutation = "Bonjour"


def main():
    # We first talk to a French customer.
    french_greeting = handle_visit(FrenchCustomer())

    # Now get a greeting for regular customers.
    regular_greeting = handle_visit(Customer())
    return french_greeting, regular_greeting
