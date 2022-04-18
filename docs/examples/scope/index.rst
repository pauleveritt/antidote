*****
Scope
*****

We manually provided the current customer and thus removed ``@inject`` from our ``greeting``.
Let's bring that back by using an Antidote "scope."

Each customer *visit* is like a separate, temporary transaction -- or in web terms, a request.
Let's add the concept of ``Visit`` to our framework.
Like a web request, it will store information from the outside world.
We register a ``VisitHandler`` factory, scoped to a visit, to let you store data from outside the system.

.. literalinclude:: framework.py

Our local site now makes two calls to ``handle_visit`` which get the outside state (which customer we are greeting) into the system for use by ``greeting`` et al.:

.. literalinclude:: __init__.py

Analysis
========

The ``Visit`` is like a ``Request`` object in web frameworks, which store things from the HTTP request.
We added a dataclass for this, for the moment storing just the current ``Customer``.
It's immutable -- we discard it from visit to visit -- so we use ``frozen=True``.

Alas, we need a place to store each ``Visit``.
We add a ``@factory`` named ``VisitHandler`` that lets us store/replace the ``Visit``.
We then mark this factory as ``scope=VISIT_SCOPE``, which has two effects:

- Whenever we reset the scope, all the data is helpfully thrown out
- Anything that depends on instances of this factory will also have their cache copied removed

TODO Is the last bullet above true? My test indicated "no".

With this in place, we add a ``visit_handler`` which is like the request processor in a web framework.

Finally, we change ``greeting`` to inject the ``Visit`` via the ``VisitHandler``.
The ``Visit`` has the current ``Customer`` which we need to find the correct ``Greeter``.

Full code: :download:`__init__.py`, :download:`framework.py`, and :download:`test_scope.py`.