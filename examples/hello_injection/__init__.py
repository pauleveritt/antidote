"""Smallest example of injection."""

from antidote import inject, service


@service
class Greeter:
    salutation: str = "Hello"


@inject
def greeting(greeter: Greeter = inject.me()) -> str:
    """Get a ``Greeter`` and return a greeting."""
    return f'{greeter.salutation}!'


def main() -> str:
    """Main entry point for this example."""
    return greeting()
