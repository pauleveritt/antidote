"""Use a factory function to integrate external classes."""
from dataclasses import dataclass

from antidote import inject, service, factory, Constants, const
from .library import Greeting


class Config(Constants):
    """Global settings for this app."""
    PUNCTUATION: str = const("!")


@factory
def default_greeting(punctuation: str = Config.PUNCTUATION) -> Greeting:
    return Greeting(punctuation=punctuation)


@service
@dataclass
class Greeter:
    name: str = "Marie"
    greeting: Greeting = inject.me(source=default_greeting)


@inject
def greeting(
    greeter: Greeter = inject.me(),
) -> str:
    """Get a ``Greeter`` and return a greeting."""
    g = greeter.greeting
    return f'{g.salutation}, my name is {greeter.name}{g.punctuation}'


def main():
    return greeting()
