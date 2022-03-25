from __future__ import annotations

import inspect
import itertools
from typing import Any, Callable, cast, List, Optional, Type, TypeVar, Union

from typing_extensions import get_args, get_origin, get_type_hints, TypeAlias

from ._provider import ConstraintsAlias, InterfaceProvider
from .predicate import NeutralWeight, Predicate, PredicateConstraint, PredicateWeight
from ..._internal import API, LazyDispatch
from ..._internal.utils import enforce_subclass_if_possible
from ...core import inject
from ...core.exceptions import DuplicateDependencyError

__all__ = ['register_predicate_merge', 'register_predicate_constraint_merge',
           'create_constraints', 'register_interface', 'register_implementation']

T = TypeVar('T')
C = TypeVar('C', bound=type)

P = TypeVar('P', bound=Predicate[Any])
PC = TypeVar('PC', bound=PredicateConstraint[Any])
Weight = TypeVar('Weight', bound=PredicateWeight)

AnyP: TypeAlias = Predicate[Any]
AnyPC: TypeAlias = PredicateConstraint[Any]

__predicate_merge: LazyDispatch[Type[AnyP], Callable[[AnyP, AnyP], AnyP]] = \
    LazyDispatch(name="predicate_merge")
__constraints_merge: LazyDispatch[Type[AnyPC], Callable[[AnyPC, AnyPC], AnyPC]] = \
    LazyDispatch(name="predicate_constraint_merge")


@API.private
def __validate_and_retrieve_return_type(func: object,
                                        expected: type
                                        ) -> Callable[[Callable[..., T]], Type[T]]:
    if not inspect.isfunction(func):
        raise TypeError(f"Expected a function, not a {type(func)!r}")
    if "return" not in func.__annotations__:
        raise TypeError(f"Missing {expected.__name__} return type hint")

    def get_return_type(f: Callable[..., T]) -> Type[T]:
        return_type = get_type_hints(f).get('return')
        # Checked at registration
        assert return_type is not None
        if not issubclass(return_type, expected):
            raise TypeError(f"Expected a {expected.__name__}, but got {return_type!r}")
        return cast(Type[T], return_type)

    return get_return_type


@API.private
def register_predicate_merge(f: Callable[[P, P], P]) -> None:
    __predicate_merge.register(__validate_and_retrieve_return_type(f, Predicate),
                               cast(Callable[[AnyP, AnyP], AnyP], f))


@API.private
def register_predicate_constraint_merge(f: Callable[[PC, PC], PC]) -> None:
    __constraints_merge.register(__validate_and_retrieve_return_type(f, PredicateConstraint),
                                 cast(Callable[[AnyPC, AnyPC], AnyPC], f))


@API.private
def create_constraints(
        *_constraints: PredicateConstraint[Any],
        qualified_by: Optional[object | list[object]] = None,
        qualified_by_one_of: Optional[list[object]] = None,
        qualified_by_instance_of: Optional[type] = None
) -> ConstraintsAlias:
    from .qualifier import QualifiedBy

    # Validate constraints
    constraints: list[PredicateConstraint[Any]] = []
    for constraint in _constraints:
        if not isinstance(constraint, PredicateConstraint):
            raise TypeError(f"Expected a PredicateConstraint, not a {type(constraint)}")
        constraints.append(constraint)

    # Create constraints from kwargs
    if qualified_by is not None:
        if isinstance(qualified_by, list):
            constraints.append(QualifiedBy(*cast(List[object], qualified_by)))
        else:
            constraints.append(QualifiedBy(qualified_by))

    if not (qualified_by_one_of is None or isinstance(qualified_by_one_of, list)):
        raise TypeError(f"qualified_by_one_of should be None or a list, "
                        f"not {type(qualified_by_one_of)!r}")
    if qualified_by_one_of:
        constraints.append(QualifiedBy.one_of(*qualified_by_one_of))

    if qualified_by_instance_of is not None:
        constraints.append(QualifiedBy.instance_of(qualified_by_instance_of))

    # Remove duplicates and combine constraints when possible
    constraints_groups: dict[
        Type[PredicateConstraint[Any]], list[PredicateConstraint[Any]]] = dict()
    for constraint in constraints:
        tpe = type(constraint)
        previous = constraints_groups.setdefault(tpe, [])
        merge = __constraints_merge.get(tpe)
        if merge is not None and len(previous) > 0:
            previous[0] = merge(previous[0], constraint)
        else:
            previous.append(constraint)

    # Extract associated predicate from the type hints
    result: ConstraintsAlias = list()
    for contraint in itertools.chain.from_iterable(constraints_groups.values()):
        predicate_type_hint = get_type_hints(contraint.evaluate).get('predicate')
        if predicate_type_hint is None:
            raise TypeError(f"Missing 'predicate' argument on the predicate filter {contraint}")

        if get_origin(predicate_type_hint) is not Union:
            raise TypeError("Predicate type hint must be Optional[P] with P being a Predicate")
        args = cast(Any, get_args(predicate_type_hint))
        if not (len(args) == 2 and (isinstance(None, args[1]) or isinstance(None, args[0]))):
            raise TypeError("Predicate type hint must be Optional[P] with P being a Predicate")

        predicate_type = args[0] if isinstance(None, args[1]) else args[1]
        if not (isinstance(predicate_type, type) and issubclass(predicate_type, Predicate)):
            raise TypeError("Predicate type hint must be Optional[P] with P being a Predicate")
        result.append((cast(Type[Predicate[Any]], predicate_type), contraint))

    return result


@API.private
@inject
def register_interface(__interface: C,
                       *,
                       provider: InterfaceProvider = inject.me()
                       ) -> C:
    if not isinstance(__interface, type):
        raise TypeError(f"Expected a class for the interface, got a {type(__interface)!r}")

    provider.register(__interface)
    return cast(C, __interface)


@API.private
@inject
def register_implementation(*,
                            interface: type,
                            implementation: C,
                            predicates: List[Union[Predicate[Weight], Predicate[NeutralWeight]]],
                            provider: InterfaceProvider = inject.me()
                            ) -> C:
    from ...service import service

    if not isinstance(interface, type):
        raise TypeError(f"Expected a class for the interface, got a {type(interface)!r}")
    if not isinstance(implementation, type):
        raise TypeError(f"Expected a class for the implementation, got a {type(implementation)!r}")
    enforce_subclass_if_possible(implementation, interface)

    # Remove duplicates and combine predicates when possible
    distinct_predicates: dict[Type[Predicate[Any]], Predicate[Any]] = dict()
    for predicate in predicates:
        if not isinstance(predicate, Predicate):
            raise TypeError(f"Expected an instance of Predicate, not a {type(predicate)!r}")

        key = type(predicate)
        previous = distinct_predicates.get(key)
        if previous is not None:
            reducer = __predicate_merge.get(key)
            if reducer is None:
                raise RuntimeError(f"Cannot have multiple predicates of type {key!r} "
                                   f"without declaring a reducer!")
            distinct_predicates[key] = reducer(previous, predicate)
        else:
            distinct_predicates[key] = predicate

    provider.register_implementation(
        interface=interface,
        dependency=implementation,
        predicates=list(distinct_predicates.values())
    )

    try:
        return cast(C, service(implementation))
    except DuplicateDependencyError:
        return cast(C, implementation)
