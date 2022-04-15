"""Get a dependency manually rather than via injection."""

from antidote import inject, service, world


@service
class Greeter:
    salutation: str = "Hello"


# No longer uses injection.
def greeting() -> str:
    """Get a ``Greeter`` and return a greeting."""
    greeter = world.get(Greeter)
    return f'{greeter.salutation}!'


def main() -> str:
    """Main entry point for this example."""
    return greeting()
