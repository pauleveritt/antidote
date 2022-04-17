========
Examples
========

Let's learn Antidote by gradually writing a pluggable application.
Each example is fully-runnable code, with a small test, along with narrative documentation.

For the scenario, imagine a ``MegaStore`` chain of stores.
Each store greets customers as they come in.
``MegaStore`` provides a system for doing so, with defaults at the corporate level.
But each store can change some of the defaults, to make it more local to the area.
In fact, each greeter can personalize the greeting.

- ``App`` is what ``MegaStore`` provides to each store
- ``Store`` is what each individual store deploys
- ``Customer`` is someone who walks in
- ``Greeter`` is someone who meets the Customer
- ``Greeting`` is what they say to the Customer
- ``Config`` provides common settings such as the punctuation on the greeting

Clever readers might spot that this parallels web applications:

- ``App`` is a framework
- ``Store`` is a site that uses that framework
- ``Customer`` is an HTTP request
- ``Greeter`` is a view
- ``Greeting`` is a response

The only thing missing is ``Plugin``, where third-parties can distribute cool stuff atop the framework, consumed and customized by a site.

.. toctree::
    :maxdepth: 1
    :caption: Example Listing

    hello_injection/index
    manual_dependency/index
    injection_flavors/index
    singletons/index

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

