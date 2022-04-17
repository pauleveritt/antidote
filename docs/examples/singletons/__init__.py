"""Services are singletons by default."""
from random import randint

from antidote import service, world


@service
class Greeter:
    salutation: str = "Hello"


@service(singleton=False)
class MultiGreeter:
    salutation: str

    def __init__(self):
        self.salutation = f"Hello {randint(0, 1000)}"


def main() -> Greeter:
    """Main entry point for this example."""
    return world.get(Greeter)
