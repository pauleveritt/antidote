"""Override a service defined in the framework."""
from antidote import implements
from .framework import Greeter, greeting


@implements(Greeter)
class SiteGreeter(Greeter):
    """Replace the bundled ``Greeter`` with a site customization."""
    name: str = "Marie"
    salutation: str = "Hi"


def main():
    return greeting()
