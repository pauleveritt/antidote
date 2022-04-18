from dataclasses import dataclass
from typing import Optional

from antidote import implements, interface, world, inject, factory, Inject
from antidote.lib.interface import NeutralWeight

CONTEXT_SCOPE = world.scopes.new(name="visit3")


@interface()
class Alert:
    name: str


@dataclass(frozen=True)
class Context:
    locale: str


@factory(scope=CONTEXT_SCOPE)
class ContextHandler:
    def __init__(self):
        self.__context = None

    def __call__(self) -> Context:
        assert self.__context is not None
        return self.__context

    def set_locale(self, locale: str) -> None:
        self.__context = Context(locale=locale)
        world.scopes.reset(CONTEXT_SCOPE)


@dataclass
class LocaleIs:
    name: str

    def matches_locale(self, locale: str) -> bool:
        return self.name == locale

    def weight(self) -> NeutralWeight:
        return NeutralWeight()


@dataclass
class ContextAttr:
    """A matcher for any attribute on the scope's ``Context``."""
    attr_name: str = "locale"

    def evaluate(self, predicate: Optional[LocaleIs]) -> bool:
        context = world.get(Context, source=ContextHandler)
        attr_value = getattr(context, self.attr_name)

        if predicate is None:
            return False
        return predicate.matches_locale(attr_value)


@implements(Alert).when(LocaleIs('en'))
class EnglishAlert(Alert):
    name: str = "English Alert"


@implements(Alert).when(LocaleIs('fr'))
class FrenchAlert(Alert):
    name: str = "French Alert"


@inject
def greeting(alert: Alert = inject.impl(ContextAttr("locale"))) -> str:
    return alert.name


@inject
def handle_visit(
    *,
    context_handler: Inject[ContextHandler],
    locale: str = "en"
) -> str:
    """Reset scope to use current customer and return greeting."""
    context_handler.set_locale(locale=locale)
    return greeting()


if __name__ == '__main__':
    # assert world.get[Alert].all() == [world.get(EngAlert)]
    print(handle_visit())
    print(handle_visit(locale="fr"))
