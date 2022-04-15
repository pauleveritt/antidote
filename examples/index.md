# Examples

## Hello Injection

Also shows writing a test that doesn't use the injector.
Explain the concept of a dependency.

## Get Dependency Manually

Rather than injecting the ``Greeter`` via the function parameter, use the ``world`` variable to imperatively get one.

## Injection Flavors

The first example used ``inject.me`` to state a dependency.
Let's see a number of other syntaxes for doing so.

## Singletons

By default, ``@service`` returns a singleton.
Meaning, there can only be one instance object in the application -- every call returns the same object.
You can customize this.

## Datclasses

We can write our services as dataclasses.

## Constants

Lazily evaluated.

## Chained Injection

Injection can depend on something which depends on something.

## Factories

Use service when it's a class you control.
For "foreign" classes, or when you want a lot of control over construction without using wiring, use factory.
This example adds ``framework.py`` to simulate something which provides a class to inject.

``Greeter`` now says, during injection, where to get the ``Greeting`` from.
Our factory function does the glue to Antidote, getting the config information and passing to the foreign class.

## Override

We still have ``framework.py`` but now it has the Greeter and Greeting.
Here we show how to transparently override a built-in service simply by registering a service later.
In this case, the service is a transitive dependency.

To do so, we need symbols that don't point to specific implementations.
Antidote provides an interface.



