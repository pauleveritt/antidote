import collections.abc as c_abc
import inspect
from typing import Callable, Iterable, Union

from .._internal.argspec import Arguments
from ..core import DEPENDENCIES_TYPE, DependencyContainer, inject


def wire(class_: type = None,
         *,
         methods: Iterable[str],
         dependencies: DEPENDENCIES_TYPE = None,
         use_names: Union[bool, Iterable[str]] = None,
         use_type_hints: Union[bool, Iterable[str]] = None,
         wire_super: Union[bool, Iterable[str]] = None,
         container: DependencyContainer = None,
         ignore_missing: bool = False
         ) -> Union[Callable, type]:
    """Wire a class by injecting the dependencies in all specified methods.

    Args:
        class_: class to wire.
        methods: Name of the methods for which dependencies should be
            injected. Defaults to all defined methods.
        dependencies: Can be either a mapping of arguments name to their
            dependency, an iterable of dependencies or a function which returns
            the dependency given the arguments name. If an iterable is specified,
            the position of the arguments is used to determine their respective
            dependency. An argument may be skipped by using :code:`None` as a
            placeholder. Type hints are overridden. Defaults to :code:`None`.
        use_names: Whether or not the arguments' name should be used as their
            respective dependency. An iterable of argument names may also be
            supplied to restrict this to those. Defaults to :code:`False`.
        use_type_hints: Whether or not the type hints (annotations) should be
            used as the arguments dependency. An iterable of argument names may
            also be specified to restrict this to those. Any type hints from
            the builtins (str, int...) or the typing (:py:class:`~typing.Optional`,
            ...) are ignored. Defaults to :code:`True`.
        wire_super: If a method from a super-class needs to be wired, specify
            either a list of method names or :code:`True` to enable it for
            all methods. Defaults to :code:`False`, only methods defined in the
            class itself can be wired.
        container: :py:class:~.core.base.DependencyContainer` from which
            the dependencies should be retrieved. Defaults to the global
            core if it is defined.
        ignore_missing: Do not raise an error if a method does exist.
            Defaults to :code:`False`.

    Returns:
        Wired class or a decorator.

    """
    wire_super = wire_super if wire_super is not None else False

    if not isinstance(methods, c_abc.Iterable):
        raise TypeError("methods must be either None or an iterable.")

    methods = set(methods)
    if isinstance(wire_super, c_abc.Iterable):
        wire_super = set(wire_super)
        if not wire_super.issubset(methods):
            raise ValueError(
                "Method names {!r} are not specified "
                "not specified in methods".format(wire_super - methods)
            )
    elif not isinstance(wire_super, bool):
        raise TypeError("wire_super must be either a boolean "
                        "or an iterable of method names.")

    if not isinstance(ignore_missing, bool):
        raise TypeError("ignore_missing must be a boolean, "
                        "not a {!r}".format(type(ignore_missing)))

    def wire_methods(cls):
        nonlocal methods

        if not inspect.isclass(cls):
            raise TypeError("Expecting a class, got a {}".format(type(cls)))

        if isinstance(dependencies, c_abc.Iterable) \
                and not isinstance(dependencies, c_abc.Mapping) \
                and len(methods) > 1:
            raise ValueError("wire does not support an iterable for `dependencies` "
                             "when multiple methods are injected.")

        for method_name in methods:
            if wire_super is True \
                    or (isinstance(wire_super, set) and method_name in wire_super):
                for c in cls.__mro__:
                    wrapped = c.__dict__.get(method_name)
                    if wrapped is not None:
                        break
                else:
                    continue  # cannot happen  # pragma: no cover
            else:
                wrapped = cls.__dict__.get(method_name)

            if wrapped is None:
                if ignore_missing is True:
                    continue
                else:
                    raise TypeError("{!r} does not have a method "
                                    "named {!r}".format(cls, method_name))

            _dependencies = dependencies
            _use_names = use_names
            _use_type_hints = use_type_hints

            arguments = Arguments.from_callable(
                wrapped.__func__
                if isinstance(wrapped, (staticmethod, classmethod)) else
                wrapped
            )

            if isinstance(dependencies, dict):
                _dependencies = {
                    arg_name: dependency
                    for arg_name, dependency in dependencies.items()
                    if arg_name in arguments
                }
                if not _dependencies:
                    _dependencies = None

            if isinstance(use_names, c_abc.Iterable):
                _use_names = [name
                              for name in use_names
                              if name in arguments]
                if not _use_names:
                    _use_names = False

            if isinstance(use_type_hints, c_abc.Iterable):
                _use_type_hints = [name
                                   for name in use_type_hints
                                   if name in arguments]
                if not _use_type_hints:
                    _use_type_hints = False

            injected_wrapped = inject(wrapped,
                                      arguments=arguments,
                                      dependencies=_dependencies,
                                      use_names=_use_names,
                                      use_type_hints=_use_type_hints,
                                      container=container)

            if injected_wrapped is not wrapped:  # If something has changed
                setattr(cls, method_name, injected_wrapped)

        return cls

    return class_ and wire_methods(class_) or wire_methods
