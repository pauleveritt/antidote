from __future__ import annotations

from dataclasses import dataclass, field

from antidote import inject, service, Inject, world, factory

REQUEST_SCOPE = world.scopes.new(name="request")


@dataclass
class Request:
    shirt_color: str = field(default="blue")

    def __post_init__(self):
        print("\n\n### Making a new request")


@factory(scope=REQUEST_SCOPE)
class RequestHandler:
    def __init__(self):
        self.__request = None

    def __call__(self) -> Request:
        assert self.__request is not None
        return self.__request

    def set_request(self, shirt_color: str) -> None:
        self.__request = Request(shirt_color=shirt_color)
        world.scopes.reset(REQUEST_SCOPE)


@service
@dataclass
class Config:
    punctuation: str = "!"

    def __post_init__(self):
        print("\n\n#### Making Config")


@service()
@dataclass
class Greeter:
    """Someone that says hello to a customer."""
    config: Inject[Config]
    request: Request = inject.me(source=RequestHandler)
    salutation: str = "Hello"

    def __post_init__(self):
        print("\n\n#### Making Greeter")


@inject
def greeting(greeter: Greeter = inject.me()) -> str:
    """Get a ``Greeter`` and return a greeting."""
    return f'{greeter.salutation}{greeter.config.punctuation}'


@inject
def handle_request(
    color: str,
    request_handler: RequestHandler = inject.me()
):
    request_handler.set_request(shirt_color=color)
    return greeting()


def main():
    print(handle_request("red"))
    print(handle_request("green"))


if __name__ == '__main__':
    main()
