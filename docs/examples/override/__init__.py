"""Override a service defined in the framework."""
from antidote import implements
from .framework import Greeter, greeting


@implements(Greeter)
class SiteGreeter(Greeter):
    """Replace the bundled ``Greeter`` with a site customization."""
    salutation: str = "The custom alert"


def main() -> str:
    """Main entry point for this example."""
    return greeting()
