"""Test this example."""
from . import main, Greeter, greeting


def test_uninjected() -> None:
    """Use our function without the injector."""
    greeter = Greeter()
    assert greeting(greeter) == "Hello!"


def test_main() -> None:
    """Ensure the injected result matches what is expected."""
    assert main() == "Hello!"
