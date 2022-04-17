**********
Datclasses
**********

We can write our services as dataclasses.
This can help reduce class-writing boilerplate in all the dataclass-y ways.

.. literalinclude:: __init__.py

Analysis
========

You'll find some times `where things don't work as expected <https://github.com/Finistere/antidote/issues/39>`_ on dataclass fields.
The reasons though are easy-to-understand and work around.
It's possible that dataclass fields provide extra developer productivity for Antidote in the future.

Full code: :download:`__init__.py` and :download:`test_use_dataclasses.py`.