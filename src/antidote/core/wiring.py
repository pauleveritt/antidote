from __future__ import annotations

import collections.abc as c_abc
import enum
import warnings
from typing import (Callable, FrozenSet, Iterable, Optional, overload, TypeVar, Union)

from typing_extensions import final

from .injection import AUTO_PROVIDE_TYPE, DEPENDENCIES_TYPE, validate_injection
from .._internal import API
from .._internal.utils import Copy, FinalImmutable

C = TypeVar('C', bound=type)
_empty_set: FrozenSet[str] = frozenset()


class Methods(enum.Enum):
    ALL = enum.auto()


@API.public
@final
class Wiring(FinalImmutable):
    """
    Defines how a class should be wired, meaning if/how/which methods are injected. This
    class is intended to be used by configuration objects. If you just want to wire a
    single class, consider using the class decorator :py:func:`~.wire` instead. There are
    two purposes:

    - providing a default injection which can be overridden either by changing the wiring
      or using `@inject` when using :code:`attempt_methods`.
    - wiring of multiple methods with similar dependencies.

    Instances are immutable. If you want to change some parameters, typically defaults
    defined by Antidote, you'll need to rely on :py:meth:`~.copy`. It accepts the same
    arguments as :py:meth:`~.__init__` and overrides existing values.

    .. doctest:: core_Wiring

        >>> from antidote import Wiring, Service, Provide
        >>> wiring = Wiring(methods=['my_method'])
        >>> class Database(Service):
        ...     pass
        >>> @wiring.wire
        ... class Dummy:
        ...     def my_method(self, db: Provide[Database]) -> Database:
        ...         return db
        >>> Dummy().my_method()
        <Database ...>


    """
    __slots__ = ('methods', 'auto_provide', 'dependencies',
                 'raise_on_double_injection')
    methods: Union[Methods, FrozenSet[str]]
    """Method names that must be injected."""
    dependencies: DEPENDENCIES_TYPE
    auto_provide: API.Deprecated[Union[bool, FrozenSet[type], Callable[[type], bool]]]
    raise_on_double_injection: bool

    def __init__(self,
                 *,
                 methods: Union[Methods, Iterable[str]] = Methods.ALL,
                 dependencies: DEPENDENCIES_TYPE = None,
                 auto_provide: API.Deprecated[AUTO_PROVIDE_TYPE] = None,
                 raise_on_double_injection: bool = False) -> None:
        """
        Args:
            methods: Names of methods to be injected. If any of them is already injected,
                an error will be raised. Consider using :code:`attempt_methods` otherwise.
            dependencies: Propagated for every method to :py:func:`~.injection.inject`
            auto_provide:
                .. deprecated:: 1.1

                Propagated for every method to :py:func:`~.injection.inject`

        """
        if not isinstance(raise_on_double_injection, bool):
            raise TypeError(f"raise_on_double_injection must be a boolean, "
                            f"not {type(raise_on_double_injection)}")

        if auto_provide is not None:
            warnings.warn("Using auto_provide is deprecated.", DeprecationWarning)

        if auto_provide is None:
            auto_provide = False
        if isinstance(auto_provide, str) \
                or not (isinstance(auto_provide, (c_abc.Iterable, bool))
                        or callable(auto_provide)):
            raise TypeError(f"auto_provide must be an iterable of method names, "
                            f"not {type(auto_provide)}.")
        if isinstance(auto_provide, c_abc.Iterable):
            auto_provide = frozenset(auto_provide)

        if isinstance(methods, str) or not isinstance(methods, (c_abc.Iterable, Methods)):
            raise TypeError(f"methods must be an iterable of method names, "
                            f"not {type(methods)}.")
        elif isinstance(methods, c_abc.Iterable):
            methods = frozenset(methods)
            if not all(isinstance(method, str) for method in methods):
                raise TypeError("methods is expected to contain methods names (str)")

        if not isinstance(auto_provide, str) and isinstance(auto_provide,
                                                            c_abc.Iterable):
            auto_provide = frozenset(auto_provide)
        validate_injection(dependencies, auto_provide)

        super().__init__(methods=methods,
                         dependencies=dependencies,
                         auto_provide=auto_provide,
                         raise_on_double_injection=raise_on_double_injection)

    def copy(self,
             *,
             methods: Union[Methods, Iterable[str], Copy] = Copy.IDENTICAL,
             dependencies: Union[DEPENDENCIES_TYPE, Copy] = Copy.IDENTICAL,
             auto_provide: API.Deprecated[Union[AUTO_PROVIDE_TYPE, Copy]] = Copy.IDENTICAL,
             raise_on_double_injection: Union[bool, Copy] = Copy.IDENTICAL
             ) -> Wiring:
        """
        Copies current wiring and overrides only specified arguments.
        Accepts the same arguments as :py:meth:`.__init__`
        """
        return Copy.immutable(self,
                              methods=methods,
                              dependencies=dependencies,
                              auto_provide=auto_provide,
                              raise_on_double_injection=raise_on_double_injection)

    def wire(self, __klass: C) -> C:
        """
        Used to wire a class with specified configuration.

        Args:
            __klass: Class to wired

        Returns:
            The same class object with specified methods injected.
        """
        from ._wiring import wire_class
        return wire_class(__klass, self)


@overload
def wire(__klass: C,
         *,
         methods: Union[Methods, Iterable[str]] = Methods.ALL,
         dependencies: DEPENDENCIES_TYPE = None,
         auto_provide: API.Deprecated[AUTO_PROVIDE_TYPE] = None,
         raise_on_double_injection: bool = False
         ) -> C:
    ...  # pragma: no cover


@overload
def wire(*,
         methods: Union[Methods, Iterable[str]] = Methods.ALL,
         dependencies: DEPENDENCIES_TYPE = None,
         auto_provide: API.Deprecated[AUTO_PROVIDE_TYPE] = None,
         raise_on_double_injection: bool = False
         ) -> Callable[[C], C]:
    ...  # pragma: no cover


@API.public
def wire(__klass: Optional[C] = None,
         *,
         methods: Union[Methods, Iterable[str]] = Methods.ALL,
         dependencies: DEPENDENCIES_TYPE = None,
         auto_provide: API.Deprecated[AUTO_PROVIDE_TYPE] = None,
         raise_on_double_injection: bool = False
         ) -> Union[C, Callable[[C], C]]:
    """
    Wire a class by injecting specified methods. This avoids repetition if similar
    dependencies need to be injected in different methods. Methods will only be wrapped
    if and only if Antidote may inject a dependency in it, like :py:func:`.inject`.

    Args:
        raise_on_double_injection: Whether an error should be raised if method is already
            injected. Defaults to :py:obj:`False`.
        __klass: Class to wire.
        methods: Names of methods that must be injected. Defaults to all method
        dependencies: Propagated for every method to :py:func:`~.injection.inject`.
        auto_provide:
            Propagated for every method to :py:func:`~.injection.inject`.
            .. deprecated:: 1.1

    Returns:
        Wired class or a class decorator.

    """
    wiring = Wiring(
        methods=methods,
        dependencies=dependencies,
        auto_provide=auto_provide,
        raise_on_double_injection=raise_on_double_injection
    )

    def wire_methods(cls: C) -> C:
        from ._wiring import wire_class
        return wire_class(cls, wiring)

    return __klass and wire_methods(__klass) or wire_methods


W = TypeVar('W', bound='WithWiringMixin')


@API.private  # Inheriting this class yourself is not part of the public API
class WithWiringMixin:
    __slots__ = ()

    wiring: Optional[Wiring]

    def copy(self: W, *, wiring: Union[Optional[Wiring], Copy] = Copy.IDENTICAL) -> W:
        raise NotImplementedError()  # pragma: no cover

    @API.public
    def with_wiring(self: W,
                    *,
                    methods: Union[Methods, Iterable[str], Copy] = Copy.IDENTICAL,
                    dependencies: Union[DEPENDENCIES_TYPE, Copy] = Copy.IDENTICAL,
                    auto_provide: API.Deprecated[Union[AUTO_PROVIDE_TYPE, Copy]] = Copy.IDENTICAL,
                    raise_on_double_injection: Union[bool, Copy] = Copy.IDENTICAL,
                    ) -> W:
        """
        Accepts the same arguments as :py:class:`.Wiring`. Its only purpose is to provide
        a easier way to change the wiring:

        .. code-block:: python

            conf.with_wiring(dependencies={})
            # instead of
            conf.copy(wiring=conf.wiring.copy(dependencies={}))

        """
        if self.wiring is None:
            return self.copy(wiring=Wiring().copy(
                methods=methods,
                dependencies=dependencies,
                auto_provide=auto_provide,
                raise_on_double_injection=raise_on_double_injection))
        else:
            return self.copy(wiring=self.wiring.copy(
                methods=methods,
                dependencies=dependencies,
                auto_provide=auto_provide,
                raise_on_double_injection=raise_on_double_injection))
