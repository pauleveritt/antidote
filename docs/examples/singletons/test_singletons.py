from antidote import world
from . import main, Greeter, MultiGreeter


def test_main():
    main_greeter = main()
    not_another_greeter = world.get(Greeter)
    assert main_greeter is not_another_greeter  # The same


def test_not_singleton():
    """``MultiGreeter`` is defined as not a singleton."""
    first: MultiGreeter = world.get(MultiGreeter)
    next_: MultiGreeter = world.get(MultiGreeter)
    assert first is not next_
    assert first.salutation is not next_.salutation
