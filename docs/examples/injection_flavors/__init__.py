"""Use other syntaxes to mark a dependency."""
from typing import Optional

from antidote import inject, service, Inject


@service
class Greeter:
    salutation: str = "Hello"


class MissingGreeter:
    """Not registered with ``@service``."""
    salutation: str = "Missing Hello"


@inject
def annotation_greeting(greeter: Inject[Greeter]) -> str:
    """Use a PEP 593 ``Annotation``, in this case, ``Inject``."""
    return f'{greeter.salutation}!'


@inject([Greeter])
def list_greeting(greeter: Greeter) -> str:
    """Synchronize the decorator and function arguments with a list."""
    return f'{greeter.salutation}!'


@inject(dict(greeter=Greeter))
def dict_greeting(greeter: Greeter) -> str:
    """Synchronize the decorator and function arguments with a dict."""
    return f'{greeter.salutation}!'


@inject
def optional_greeter(greeter: Optional[MissingGreeter] = inject.me()) -> str:
    """If there is no MissingGreeter registered, let it be ``None``."""
    if greeter is None:
        return "Missing!"

    return f'{greeter.salutation}!'


def main():
    return annotation_greeting(), list_greeting(), dict_greeting()
