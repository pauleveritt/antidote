from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from antidote import implements, interface, QualifiedBy, world
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
        return Weight(1000 if self.lang != 'en' else 500)

    def evaluate(self, predicate: Optional[LocaleIs]) -> bool:
        if predicate is None:
            # If no language is specified, there's just no need for it.
            return True

        return self.lang == predicate.lang or predicate.lang == 'en'


@interface()
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


if __name__ == '__main__':
    french_locale = LocaleIs("fr")
    alert = world.get[Alert].single(french_locale)
    print(alert.text())
