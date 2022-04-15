"""Override a service defined in the framework."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any

from antidote import interface, implements, QualifiedBy, world
# from .framework import Greeting, greeting
#
#
# @service
# @dataclass
# class Greeter:
#     name: str = "Marie"
#     greeting: Greeting = inject.me()
#
#
# def main() -> str:
#     """Main entry point for this example."""
#     return greeting()
from antidote.lib.interface import Predicate


@dataclass
class Weight:
    value: float

    @classmethod
    def of_neutral(cls, predicate: Optional[Predicate[Any]]) -> Weight:
        if isinstance(predicate, QualifiedBy):
            # Custom weight
            return Weight(len(predicate.qualifiers))
        return Weight(0)

    def __lt__(self, other: Weight) -> bool:
        return self.value < other.value

    def __add__(self, other: Weight) -> Weight:
        return Weight(self.value + other.value)


@dataclass
class LocaleIs:
    lang: str

    def weight(self) -> Weight:
        # Higher weight than 0, because if the language matches it should be prioritized over the
        # alternative implementations.
        # English has a lower weight because it always matches, as the default, and other languages
        # should be able to override it.
        return Weight(1000 if self.lang != 'en' else 500)

    def evaluate(self, predicate: Optional[LocaleIs]) -> bool:
        if predicate is None:
            # If no language is specified, there's just no need for it.
            return True

        return self.lang == predicate.lang or predicate.lang == 'en'


@interface
class Alert:
    def text(self) -> str:
        pass


@implements(Alert).when(LocaleIs('fr'))
class FrenchAlert(Alert):
    def text(self) -> str:
        return "Quelque chose en français!"


@implements(Alert).when(LocaleIs('en'))
class DefaultAlert(Alert):
    def text(self) -> str:
        return "Something in English!"


def main():
    assert world.get[Alert].single(LocaleIs("fr")) is world.get(FrenchAlert)
    assert world.get[Alert].single(LocaleIs("it")) is world.get(DefaultAlert)
    assert world.get[Alert].single(LocaleIs("en")) is world.get(DefaultAlert)
    return "XXX"
