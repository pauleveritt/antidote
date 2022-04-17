*********
Factories
*********

Sometimes your code uses a class that you don't control, for example from an installed library.
For example, some file ``library.py`` might provide your ``Greeting`` class:

.. literalinclude:: library.py

You can't sprinkle the Antidote magic on it without forking it.
Instead, you can use register an Antidote "@factory" to mediate:

.. literalinclude:: __init__.py

``Greeter`` now says, during injection, where to get the ``Greeting`` from.
Our factory function does the glue to Antidote, getting the config information and passing to the "foreign" class.

Analysis
========

Antidote looks at the *return type* of the function, then registers the factory for that type -- in this case, ``Greeting``.

As the :doc:`Getting Started <../../tutorial>` docs show, there's a good bit going on with factories.
The simple case is simple and convenient, but you have some more options available.

Like ``@service``, the factory instance is by default a singleton.
This can be changed with the same ``singleton=False`` decorator argument.

There might be cases where you want to use a factory function even for service classes under your own control.
Then again, Antidote provides a number of protocols to control service creation, directly on the class, with resorting to a separate factory function.

Full code: :download:`__init__.py`, :download:`library.py`, and :download:`test_factories.py`.