"""Test this example."""
from . import main, MissingGreeter, optional_greeter


def test_main() -> None:
    """Ensure the injected result matches what is expected."""
    result = "Hello!"
    assert main() == (result, result, result)


def test_optional_is_present() -> None:
    """This time provide a greeter to ``optional_greeter."""

    missing_greeter = MissingGreeter()
    result = optional_greeter(missing_greeter)
    assert result == "Missing Hello!"
