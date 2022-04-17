from . import main, Greeter, greeting


def test_main():
    assert main() == "Hello!"


def test_uninjected():
    """Use our function without the injector."""
    greeter = Greeter()
    assert greeting(greeter) == "Hello!"
