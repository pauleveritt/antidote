from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, cast, Generic, List, Optional, overload, Type, TypeVar, Union

from typing_extensions import final

from ._internal import create_constraints, register_implementation, register_interface
from ._provider import InterfaceProvider, Query
from .predicate import NeutralWeight, Predicate, PredicateConstraint, PredicateWeight
from .qualifier import QualifiedBy
from ..._internal import API
from ...core import Dependency, inject

__all__ = ['register_interface_provider', 'interface', 'implements', 'ImplementationsOf']

Itf = TypeVar('Itf', bound=type)
C = TypeVar('C', bound=type)
T = TypeVar('T')
Weight = TypeVar('Weight', bound=PredicateWeight)


@API.experimental
def register_interface_provider() -> None:
    from antidote import world
    world.provider(InterfaceProvider)


@overload
def interface(klass: C) -> C:
    ...  # pragma: no cover


@overload
def interface() -> Callable[[C], C]:
    ...  # pragma: no cover


@API.public
def interface(klass: Optional[C] = None) -> Union[C, Callable[[C], C]]:
    """
    Declares a class as an interface. One or multiple implementations can then be declared for it:

    .. doctest:: lib_interface_decorator

        >>> from antidote import interface, implements, inject, world
        >>> @interface
        ... class Service:
        ...     pass
        >>> @implements(Service)
        ... class ServiceImpl(Service):
        ...     pass
        >>> @inject
        ... def f(service: Service = inject.impl()) -> Service:
        ...     return service
        >>> f()
        <ServiceImpl ...>
        >>> world.get[Service].single()
        <ServiceImpl ...>

    Alternative implementations can be declared and one can retrieve all of them at once:

    .. doctest:: lib_interface_decorator

        >>> @implements(Service)
        ... class ServiceImplV2(Service):
        ...     pass
        >>> @inject
        ... def f(services: list[Service] = inject.impl()) -> list[Service]:
        ...     return services
        >>> f()
        [<ServiceImplV2 ...>, <ServiceImpl ...>]
        >>> world.get[Service].all()
        [<ServiceImplV2 ...>, <ServiceImpl ...>]

    However, as defined Antidote is not able to provide a single implementation anymore.

    .. doctest:: lib_interface_decorator

        >>> world.get[Service].single()
        Traceback (most recent call last):
          File "<stdin>", line 1, in ?
        DependencyInstantiationError: ...

    To enable Antidote to select one implementation among many, you need to use
    :py:class:`~.lib.interface.Predicate` and eventually
    :py:class:`~.lib.interface.PredicateConstraint`. Antidote currently only provides one kind out
    of the box :py:class:`.QualifiedBy`.

    Qualifiers can be used to narrow the candidate implementations for an interface. Qualifiers are
    matched by their :py:func:`id` and not their equality.

    .. doctest:: lib_interface_decorator_qualified_by

        >>> from enum import Enum, auto
        >>> from antidote import interface, implements, inject, world
        >>> class System(Enum):
        ...     LINUX = auto()
        ...     WINDOWS = auto()
        >>> V1 = object()
        >>> def _(x):  # Necessary for Python <3.9 (PEP 614)
        ...     return x
        >>> @interface
        ... class Command:
        ...     def execute(self) -> str:
        ...         raise NotImplementedError()
        >>> @_(implements(Command).when(qualified_by=[System.LINUX, V1]))
        ... class LinuxCommand(Command):
        ...     def execute(self) -> str:
        ...         return "Linux"
        >>> @_(implements(Command).when(qualified_by=[System.WINDOWS, V1]))
        ... class WindowsCommand(Command):
        ...     def execute(self) -> str:
        ...         return "Windows"
        >>> @inject
        ... def run_command(command: Command = inject.impl(qualified_by=System.LINUX)) -> str:
        ...     return command.execute()
        >>> run_command()
        'Linux'
        >>> world.get[Command].all(qualified_by=V1)
        [<WindowsCommand ...>, <LinuxCommand ...>]

    Antidote also provides more complex ways to select specific qualifiers such as:

    .. doctest:: lib_interface_decorator_qualified_by

        >>> world.get[Command].all(qualified_by_one_of=[System.WINDOWS, System.LINUX])
        [<WindowsCommand ...>, <LinuxCommand ...>]
        >>> world.get[Command].all(qualified_by_instance_of=System)
        [<WindowsCommand ...>, <LinuxCommand ...>]

    Args:
        klass: Interface class which implementations should implement. Implementations should
            be a subclass of it. The interface can also be a Protocol in which case type checking
            will only be enforced if :code:`runtime_checkable` is used.

    Returns:
        decorated interface class.

    """
    return klass and register_interface(klass) or register_interface


@API.private
class ImplementsWithPredicates(Generic[Itf]):
    def __init__(self,
                 __interface: Itf,
                 predicates: Optional[list[Predicate[Weight] | Predicate[NeutralWeight]]] = None
                 ) -> None:
        self._interface = __interface
        self.__predicates = predicates or []

    @API.public
    def __call__(self, klass: C) -> C:
        register_implementation(
            interface=self._interface,
            implementation=klass,
            predicates=self.__predicates
        )
        return klass


@API.public
@final
class implements(ImplementsWithPredicates[Itf]):
    def __init__(self, __interface: Itf) -> None:
        """
        Declares the decorated class to be a candidate implementation for the specified interface.
        The interface can also be a Protocol. If the interface is a regular class or a
        :py:func:`~typing.runtime_checkable` Protocol, the implementation will be type checked.

        .. doctest:: lib_interface_implements

            >>> from antidote import interface, implements, inject, world
            >>> @interface
            ... class Service:
            ...     pass
            >>> @implements(Service)
            ... class ServiceImpl(Service):
            ...     pass
            >>> @implements(Service)
            ... class BadImpl:
            ...     pass
            Traceback (most recent call last):
              File "<stdin>", line 1, in ?
            TypeError: ...


        Args:
            __interface: Interface class.
        """
        super().__init__(__interface)

    def when(self,
             *_predicates: Predicate[Weight] | Predicate[NeutralWeight],
             qualified_by: Optional[object | list[object]] = None
             ) -> ImplementsWithPredicates[Itf]:
        """
        Associate :py:class:`~.lib.interface.Predicate` with the decorated implementation. The
        implementation will only be used if all the predicates return a weight. In case multiple
        implementations are valid candidates, their ordering is determined by the total weight of
        all predicates.

        .. note::

            See :py:func:`~.interface` for examples.

        Args:
            *_predicates: Objects implementing the :py:class:`~.lib.interface.Predicate` protocol.
            qualified_by: An object, or a list of it, by which the implementation is qualified.
                Those qualifiers can then be used at runtime to narrow the possible implementations
                for an interface. Beware, qualifiers rely on the :py:func:`id` of the objects, not
                their equality.

        Returns:
            class decorator

        """
        predicates: list[Predicate[Weight] | Predicate[NeutralWeight]] = list(_predicates)
        if qualified_by is not None:
            if isinstance(qualified_by, list):
                predicates.append(QualifiedBy(*cast(List[object], qualified_by)))
            else:
                predicates.append(QualifiedBy(qualified_by))
        return ImplementsWithPredicates(self._interface, predicates)


@API.public
@final
@dataclass(frozen=True, init=False)
class ImplementationsOf(Generic[T]):
    """
    Used to construct the actual dependency for the provider handling the interfaces.

    .. doctest:: lib_interface_implementations_of

        >>> from antidote import interface, implements, inject, world, ImplementationsOf
        >>> @interface
        ... class Service:
        ...     pass
        >>> @implements(Service)
        ... class ServiceImpl(Service):
        ...     pass
        >>> world.get[Service].single()
        <ServiceImpl ...>
        >>> # the former is equivalent to:
        ... world.get(ImplementationsOf(Service).single())
        <ServiceImpl ...>

    """
    __slots__ = ('__interface',)
    __interface: Type[T]

    @inject
    def __init__(self, interface: Type[T], *, provider: InterfaceProvider = inject.me()) -> None:
        """
        Args:
            interface: Interface for which implementations should be retrieved. It must have been
                decorated with :py:func:`~.interface`.
        """
        if not isinstance(interface, type):
            raise TypeError(f"Expected a class, got a {type(interface)!r}")
        if not provider.has_interface(interface):
            raise ValueError(f"Interface {interface!r} was not decorated with @interface.")
        object.__setattr__(self, f"_{type(self).__name__}__interface", interface)

    def all(self,
            *constraints: PredicateConstraint[Any],
            qualified_by: Optional[object | list[object]] = None,
            qualified_by_one_of: Optional[list[object]] = None,
            qualified_by_instance_of: Optional[type] = None
            ) -> Dependency[list[T]]:
        """
        Construct the dependency to retrieve all implementations matching given constraints for
        the specified interface. Having no implementation matching the constraints will not raise
        an error, but instead an empty list will be retrieved.

        Args:
            *constraints: :py:class:`~.lib.interface.PredicateConstraint` to be evaluated when
                selecting the implementation.
            qualified_by: An implementation must be qualified by the specified object or all
                objects if a list is specified.
            qualified_by_one_of: An implementation must be qualified by at least one of the objects
                of the specified list.
            qualified_by_instance_of: An implementation must be qualified by object of the specified
                type.

        Returns:
            A dependency for the list of implementations matching the constraints.
        """
        query = Query(
            interface=self.__interface,
            constraints=create_constraints(
                *constraints,
                qualified_by=qualified_by,
                qualified_by_one_of=qualified_by_one_of,
                qualified_by_instance_of=qualified_by_instance_of
            ),
            all=True
        )
        return cast(Dependency[List[T]], query)

    def single(self,
               *constraints: PredicateConstraint[Any],
               qualified_by: Optional[object | list[object]] = None,
               qualified_by_one_of: Optional[list[object]] = None,
               qualified_by_instance_of: Optional[type] = None
               ) -> Dependency[T]:
        """
        Construct the dependency to retrieve a single implementation matching given constraints for
        the specified interface. If multiple or no implementation is found, an error will be raised
        upon retrieval.

        Args:
            *constraints: :py:class:`~.lib.interface.PredicateConstraint` to be evaluated when
                selecting the implementation.
            qualified_by: An implementation must be qualified by the specified object or all
                objects if a list is specified.
            qualified_by_one_of: An implementation must be qualified by at least one of the objects
                of the specified list.
            qualified_by_instance_of: An implementation must be qualified by object of the specified
                type.

        Returns:
            A dependency for the list of implementations matching the constraints.
        """
        query = Query(
            interface=self.__interface,
            constraints=create_constraints(
                *constraints,
                qualified_by=qualified_by,
                qualified_by_one_of=qualified_by_one_of,
                qualified_by_instance_of=qualified_by_instance_of
            ),
            all=False
        )
        return cast(Dependency[T], query)
