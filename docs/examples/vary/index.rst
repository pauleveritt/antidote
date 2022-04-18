****
Vary
****

We just looked two implementations for the same "thing", with the custom one overriding the built-in one.






The pluggable app in ``framework.py`` provides built-in implementations for ``Greeter`` and ``greeting``:

.. literalinclude:: framework.py

Our "site" installs this framework package but wants to use a different ``Greeter``.
We do this by registering our own implementation, using ``@implements``:

.. literalinclude:: __init__.py

Analysis
========

Lots going on here.
But it's the beginning of using Antidote for pluggable systems, where multiple implementation classes might exist for the same service.

In this case we have a concept of a ``Greeter``.
In ``framework.py`` this is represented by an interface -- that is, ``@interface`` registers the idea of a ``Greeter`` in the Antidote ``world``.
There's nothing (currently) special about it -- just make a class (so it can be a type).
The class could just have ``pass`` with no members.

Once you this ``Greeter`` concept -- an "interface" -- you can then provide implementations for it that Antidote will choose from.
The "framework" provides one in a ``DefaultGreeter`` class.
It's important for the implementation to subclass from ``Greeter``, so it will be a subtype.
Otherwise, Antidote will raise an import-time error.
TODO Even better, ``mypy`` will warn you during static analysis.

It's the line above the class that does the magic.
``@implements`` is a way to say "this class is an implmentation of that interface."
This statement is done in a way compatible with Python static type checking (which isn't easy), while also flexible.
You use the ``.when()`` clause to say in which cases Antidote should choose this implementation.

The conditions for a ``.when()`` are known as "predicates".
They are extensible.
In this case, we wrote our own, but it's likely the "overrides" pattern is common enough that Antidote will bundle its own.

With that in place, our little pluggable app has an overridable ``Greeter``.
Our usage in ``__init__.py`` simply has to say ``@implements(Greeter)`` and ``SiteGreeter`` "overrides" the ``DefaultGreeter``.

At runtime, we call ``greeting()`` which is bundled with the framework.
It depends on ``Greeting``, but we don't have to fork it to point at our new ``SiteGreeter``.
This is a powerful and useful concept for building pluggable apps.

Full code: :download:`__init__.py`, :download:`framework.py`, and :download:`test_override.py`.