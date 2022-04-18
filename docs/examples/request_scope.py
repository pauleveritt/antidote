from dataclasses import dataclass
from typing import Optional

from antidote import implements, interface, world, inject, factory, service
from antidote.lib.interface import NeutralWeight, Predicate

REQUEST_SCOPE = world.scopes.new(name="request")


@dataclass
class Customer:
    name: str


@dataclass
class FrenchCustomer(Customer):
    name: str


@service(scope=REQUEST_SCOPE, singleton=False)
@dataclass
class Context:
    customer: Customer


def main():
    # First request comes in, get the context, assign the customer
    context = world.get(Context)
    context.customer = Customer(name="Paul")
    greeting = world.get[Greeting].single()

    # Reset, process another request
    world.scopes.reset()
    context = world.get(Context)
    context.customer = FrenchCustomer(name="Benjamin")
    greeting = world.get[Greeting].single()


@factory(scope=REQUEST_SCOPE)
def current_customer() -> Customer:
    request = Request()
    return request


@dataclass
class Context:
    locale: str


class ContextAwarePredicate(Predicate):
    def matches_context(self, context: Context) -> bool:
        raise NotImplementedError()


@dataclass
class LocaleIs(ContextAwarePredicate):
    name: str

    def matches_context(self, context: Context) -> bool:
        return self.name == context.locale

    def weight(self) -> NeutralWeight:
        return NeutralWeight()


@dataclass
class MatchingContext:
    context: Context

    @inject
    def evaluate(self,
                 predicate: Optional[ContextAwarePredicate],
                 request: Request = inject.me(source=current_request)
                 ) -> bool:
        if predicate is None:
            return False
        return predicate.matches_context(self.context)


@interface()
class Alert:
    pass


@implements(Alert).when(LocaleIs('en'))
class EngAlert(Alert):
    pass


if __name__ == '__main__':
    assert world.get[Alert].all() == [world.get(EngAlert)]
    assert world.get[Alert].single(MatchingContext(Context(locale='en'))) is world.get(EngAlert)

    world.scopes.reset(REQUEST_SCOPE)
