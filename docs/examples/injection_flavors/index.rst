*****************
Injection Flavors
*****************

The first example used ``inject.me`` to state a dependency.
Let's see a number of other syntaxes for doing so.

.. literalinclude:: __init__.py

We can see this in use in the second test:

.. literalinclude:: test_injection_flavors.py

Analysis
========

This is really straight from the docs so we won't talk too much about it.
The ``Inject[Greeter]`` syntax is particularly attractive.

It's worth looking at the pattern represented in ``optional_greeter``.
Usually if an injectable isn't registered, the application will exit at startup time.
Marking it as optional allows a value of ``None`` if nothing was registered.

Full code: :download:`__init__.py` and :download:`test_injection_flavors.py`.