***************
Hello Injection
***************

We'll start with a very simple example of services and injection: a ``Greeter`` and a ``greeting``.

.. literalinclude:: __init__.py

It's easy to write a test which checks the output.
It's also easy to write a test which exercises our ``greeting`` function *without* this crazy magical injector.

.. literalinclude:: test_hello_injection.py

Analysis
========

Our ``main()`` function simply calls ``greeting``.
But the ``@inject`` decorator steps in between the caller and callee to do some things.
Specifically, the configured injector looks to see if the callee -- ``greeting`` -- wants to be provided a value.

As it turns out, ``greeting`` wants a ``Greeter``, because it used ``inject.me()``.
This is called a *dependency*.
It is a signal to the injector to go find the right "kind of thing" indicated by the ``greeter`` parameter's type hint.

``greeter`` wants a ``Greeter`` dependency.
Fortunately, the ``@service`` decorator registered a ``Greeter``.
The injector makes a ``Greeter`` instance and passes it as an argument when it calls ``greeting``.

This small example emphasizes the main point: callers and callees are decoupled.
You can then extend a system without forking either side.

Full code: :download:`__init__.py` and :download:`test_hello_injection.py`.