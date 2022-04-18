****
Vary
****

We just looked two implementations for the same "thing", with the custom one overriding the built-in one.
What if we wanted use *either* implementation based on circumstances?

Imagine the store wants a special greeter for French customers.
All other customers should get the regular company-provided greeter.
We start with a ``framework.py`` with a ``Greeter`` interface and a ``DefaultGreeter`` implementation:

.. literalinclude:: framework.py

The local site has a ``FrenchGreeter`` for each ``FrenchCustomer``:

.. literalinclude:: __init__.py

Analysis
========

The biggest change here is actually in ``greeting``.
It is no longer marked with ``@inject``.
It instead uses manual dependency injection, acting as a dispatcher based on the passed-in customer type.
As such, it is called "per-request".
We'll show later how to get each ``Customer`` into the ``world`` to let it be injected.

Each ``Greeter`` implementation must be a subclass of ``Greeter``.
Otherwise you'll get an Antidote error at startup.
We'll see in the next section how to use protocols to avoid the need to subclass.

Note that ``QualifiedBy`` is a mandatory, exact match on the provided value.
We'll look in future sections on more flexible predicates.

What if we didn't register ``FrenchGreeter``?
Since ``FrenchCustomer`` is a type of ``Customer``, would ``DefaultGreeter`` match it?
No, because ``QualifiedBy`` uses an ``isinstance`` check.
You would write a modified ``QualifiedBy`` which used typing.


Full code: :download:`__init__.py`, :download:`framework.py`, and :download:`test_vary.py`.