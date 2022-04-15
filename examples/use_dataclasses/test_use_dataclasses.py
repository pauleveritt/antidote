"""Test this example."""
from . import main


def test_main() -> None:
    """Ensure the injected result matches what is expected."""
    assert main() == "Hello!"
