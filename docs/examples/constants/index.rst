*********
Constants
*********

Your services almost always need some configuration.
Antidote provides an approach for such "constants" with extra touches for how development works.

.. literalinclude:: __init__.py

The ``Config`` class has a special ``provide_const`` protocol for Antidote.
This lets values be *optionally* retrieved from dynamic sources -- in this case, an environment variable.

The test example shows using monkeypatch to simulate putting a configuration value into the environment.

.. literalinclude:: test_constants.py

Analysis
========

Your services will likely need configuration values from a variety of sources.
Antidote's idea of ``Constants`` is an interesting take on this:

- Preserves Antidote's emphasis on strong typing, with (limited) support for runtime checking
- Differentiates between a value coming from the constant's class vs. instance
- Lazy evaluation as needed

Full code: :download:`__init__.py` and :download:`test_constants.py`.