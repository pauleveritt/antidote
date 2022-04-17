"""Override a service defined in the framework."""
from antidote import implements, world
from .framework import Alert


@implements(Alert)
class CustomAlert(Alert):
    name = "The custom alert"


def main() -> str:
    """Main entry point for this example."""
    site_alert: Alert = world.get[Alert].single()

    return site_alert.name
