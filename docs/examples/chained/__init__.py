"""Inject a dependency with dependency with dependency."""
from dataclasses import dataclass

from antidote import inject, service, Constants, const


class Config(Constants):
    """Global settings for this app."""
    PUNCTUATION: str = const("!")


@service
@dataclass
class Greeting:
    salutation: str = "Hello"
    punctuation: str = Config.PUNCTUATION


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


def main():
    return greeting()
