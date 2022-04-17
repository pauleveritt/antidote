*****************
Chained Injection
*****************

Injection can depend on something which depends on something.
In this example, our ``greeting`` function depends on ``Greeter``, as usual.
But ``Greeter`` depends on ``Greeting`` which depends on a configuration value.

.. literalinclude:: __init__.py

Full code: :download:`__init__.py` and :download:`test_chained.py`.