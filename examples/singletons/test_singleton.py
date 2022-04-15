"""Test this example."""
from antidote import world
from . import main, Greeter, MultiGreeter


def test_main() -> None:
    """Ensure the injected result matches what is expected."""
    main_greeter = main()
    not_another_greeter = world.get(Greeter)
    assert main_greeter is not_another_greeter  # The same


def test_not_singleton() -> None:
    """``MultiGreeter`` is defined as not a singleton."""
    first: MultiGreeter = world.get(MultiGreeter)
    next: MultiGreeter = world.get(MultiGreeter)
    assert first is not next
    assert first.salutation is not next.salutation
