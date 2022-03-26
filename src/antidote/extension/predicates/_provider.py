from __future__ import annotations

import bisect
from typing import Any, Callable, cast, List, Optional, Tuple, TypeVar, Union

from typing_extensions import final, TypeAlias

from .predicate import AnyPredicateWeight, Predicate
from ..._internal.utils import FinalImmutable
from ..._internal.utils.slots import SlotsRepr
from ...core import Container, DependencyDebug, DependencyValue, Provider
from ...core.exceptions import DuplicateDependencyError

T = TypeVar('T')
ConstraintsAlias: TypeAlias = List[Tuple[type, Callable[[Optional[Any]], bool]]]


class InterfaceProvider(Provider[Union[type, 'Query']]):
    def __init__(self) -> None:
        super().__init__()
        self.__implementations: dict[type, list[ImplementationNode]] = dict()

    def clone(self: InterfaceProvider, keep_singletons_cache: bool) -> InterfaceProvider:
        provider = InterfaceProvider()
        provider.__implementations = {
            key: value.copy()
            for key, value in self.__implementations.items()
        }

        return provider

    def exists(self, dependency: object) -> bool:
        return (dependency in self.__implementations
                or (isinstance(dependency, Query)
                    and dependency.interface in self.__implementations))

    def maybe_provide(self,
                      dependency: object,
                      container: Container
                      ) -> Optional[DependencyValue]:
        if not isinstance(dependency, Query):
            dependency = Query(
                interface=cast(type, dependency),
                constraints=list(),
                all=False
            )

        try:
            implementations = reversed(self.__implementations[dependency.interface])
        except KeyError:
            return None

        if dependency.all:
            values: list[object] = []
            for impl in implementations:
                if impl.match(dependency.constraints):
                    values.append(container.get(impl))
            return DependencyValue(values)
        else:
            for impl in implementations:
                if impl.match(dependency.constraints):
                    left_impl = impl
                    while left_impl.same_weight_as_left:
                        left_impl = next(implementations)
                        if left_impl.match(dependency.constraints):
                            raise DuplicateDependencyError(
                                f"Multiple implementations match the interface "
                                f"{dependency.interface!r} for the constraints "
                                f"{dependency.constraints}: {impl!r} and {left_impl!r}")

                    return DependencyValue(container.get(impl))

        return None

    def maybe_debug(self, dependency: object) -> Optional[DependencyDebug]:
        raise RuntimeError()

    def register(self, interface: type) -> None:
        self.__implementations[interface] = list()

    def register_implementation(self,
                                interface: type,
                                dependency: object,
                                predicates: list[Predicate]) -> None:
        if len(predicates) > 0:
            weight = predicates[0].weight()
            if weight is None:
                return

            for p in predicates[1:]:
                w = p.weight()
                if w is None:
                    return
                weight += w
        else:
            weight = None
        node = ImplementationNode(
            dependency=dependency,
            predicates=predicates,
            weight=weight
        )
        implementations = self.__implementations[interface]
        pos = bisect.bisect_right(implementations, node)
        node.same_weight_as_left = pos > 0 and not (implementations[pos - 1] < node)
        implementations.insert(pos, node)


@final
class ImplementationNode(SlotsRepr):
    __slots__ = ('dependency', 'predicates', 'weight', 'same_weight_as_left')
    dependency: object
    predicates: list[Predicate]
    weight: Optional[AnyPredicateWeight]
    same_weight_as_left: bool

    def __init__(self,
                 *,
                 dependency: object,
                 predicates: list[Predicate],
                 weight: Optional[Any]
                 ) -> None:
        self.dependency = dependency
        self.predicates = predicates
        self.weight = weight

    def __lt__(self, other: ImplementationNode) -> bool:
        if other.weight is None:
            return False
        elif self.weight is None:
            return other.weight is not None
        return self.weight < other.weight

    def match(self, constraints: ConstraintsAlias) -> bool:
        for tpe, constraint in constraints:
            at_least_one = False
            for predicate in self.predicates:
                if isinstance(predicate, tpe):
                    at_least_one = True
                    if not constraint(predicate):
                        return False
            if not at_least_one:
                if not constraint(None):
                    return False
        return True


@final
class Query(FinalImmutable):
    __slots__ = ('interface', 'constraints', 'all')
    interface: type
    constraints: ConstraintsAlias
    all: bool

    def __init__(self,
                 *,
                 interface: type,
                 constraints: ConstraintsAlias,
                 all: bool
                 ) -> None:
        super().__init__(interface, constraints, all)