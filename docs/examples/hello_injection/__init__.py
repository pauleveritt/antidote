from antidote import inject, service


@service
class Greeter:
    """Someone that says hello to a customer."""
    salutation: str = "Hello"


@inject
def greeting(greeter: Greeter = inject.me()) -> str:
    """Get a ``Greeter`` and return a greeting."""
    return f'{greeter.salutation}!'


def main():
    return greeting()
