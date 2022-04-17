**********
Singletons
**********

By default, ``@service`` returns a singleton.
Meaning, there can only be one instance object in the application -- every call returns the same object.
You can customize this.

.. literalinclude:: __init__.py

This code doesn't really show it, but the second test makes it more clear:

.. literalinclude:: test_singletons.py

Analysis
========

There's actually a lot of subtlety going on here.
Does your application really need to create more than one instance?
Do the inputs to object construction vary each time something asks for the service, or all they all known at compile time or first call?
Remember, it isn't just the direct input dependencies, but the dependencies of those dependencies.

Full code: :download:`__init__.py` and :download:`test_singletons.py`.