"""A library or framework in another, foreign package."""

from dataclasses import dataclass

from antidote import inject, service, Constants, const, interface, implements


class Config(Constants):
    """Global settings for this app."""
    PUNCTUATION: str = const("!")

@interface
class Greeting:
    pass

@implements(Greeting)
@dataclass
class DefaultGreeting(Greeting):
    punctuation: str = Config.PUNCTUATION
    salutation: str = "Hello"


@service
@dataclass
class Greeter:
    name: str = "Marie"
    greeting: Greeting = inject.me()


@inject
def greeting(
    greeter: Greeter = inject.me(),
) -> str:
    """Get a ``Greeter`` and return a greeting."""
    greeting = greeter.greeting
    salutation, punctuation = greeting.salutation, greeting.punctuation
    return f'{salutation}, my name is {greeter.name}{punctuation}'
