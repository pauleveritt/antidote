"""Inject lazily-evaluated constants."""

import os
from dataclasses import dataclass
from typing import Optional, ClassVar

from antidote import inject, service, Constants, const


@dataclass
class Config(Constants):
    """Global settings for this app."""
    PUNCTUATION: ClassVar[str] = const(default="!")

    # name of the constant and the arg given to const() if any.
    def provide_const(self, name: str, arg: Optional[object]):
        """Get the value from the environ, else use default."""
        return os.environ[name]


@service
@dataclass
class Greeter:
    salutation: str = "Hello"


@inject
def greeting(
    greeter: Greeter = inject.me(),
    punctuation: str = Config.PUNCTUATION
) -> str:
    """Get a ``Greeter`` and return a greeting."""
    return f'{greeter.salutation}{punctuation}'


def main() -> str:
    """Main entry point for this example."""
    return greeting()
