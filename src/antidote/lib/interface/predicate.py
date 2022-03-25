from __future__ import annotations

from typing import Any, Callable, Optional, Type, TypeVar

from typing_extensions import final, Protocol, runtime_checkable

from ..._internal import API
from ..._internal.utils.meta import Singleton

__all__ = ['NeutralWeight', 'Predicate', 'PredicateWeight',
           'PredicateConstraint', 'predicate_typeclasses']

SelfWeight = TypeVar('SelfWeight', bound='PredicateWeight')


@API.experimental
class PredicateWeight(Protocol):
    """
    The weight defines the ordering of the implementations. When requesting all implementations,
    their ordering is the one defined by their weight. For a single implementation, it's the one
    with the highest weight. If multiple implementations have the highest weight, an exception will
    be raised when requesting a single implementation.

    A weight must define the operator :code:`<` for the ordering, :code:`+` to sum the weights of
    multiple predicates and the method :code:`of_neutral` to handle predicates with a neutral
    :py:class:~.lib.interface.NeutralWeight`.

    Mixing predicates and/or implementations with :py:class:~.lib.interface.NeutralWeight` and your
    custom weight is supported as long as your method :code:`of_neutral` can provide a weight.
    However, multiple custom weights are not.

    All methods are only called at import time, when declaring dependencies.

    .. doctest:: lib_interface_weight

        >>> from typing import Optional, Any
        >>> from antidote.lib.interface import Predicate, QualifiedBy
        >>> class Weight:
        ...     def __init__(self, value: int) -> None:
        ...         self.value = value
        ...
        ...     @classmethod
        ...     def of_neutral(cls, predicate: Optional[Predicate[Any]]) -> 'Weight':
        ...         if isinstance(predicate, QualifiedBy):
        ...             return Weight(len(predicate.qualifiers))
        ...         return Weight(0)
        ...
        ...     def __lt__(self, other: 'Weight') -> bool:
        ...         return self.value < other.value
        ...
        ...     def __add__(self, other: 'Weight') -> 'Weight':
        ...         return Weight(self.value + other.value)
    """

    @classmethod
    def of_neutral(cls: Type[SelfWeight], predicate: Optional[Predicate[Any]]) -> SelfWeight:
        """
        Called when a predicate has a :py:class:~.lib.interface.NeutralWeight` or when an
        implementation has no weight at all. In which case :py:obj:`None` is given as argument.

        Args:
            predicate: Neutral weighted predicate or None for an implementation without predicates.

        Returns:
            Weight of the predicate or implementation.
        """
        ...  # pragma: no cover

    def __lt__(self: SelfWeight, other: SelfWeight) -> bool:
        """
        Less than operator, used for the sorting of weights.

        Args:
            other: other will always be an instance of the current weight class.

        """
        ...  # pragma: no cover

    def __add__(self: SelfWeight, other: SelfWeight) -> SelfWeight:
        """
        Plus operator, used to sum weights of predicates.

        Args:
            other: other will always be an instance of the current weight class.

        """
        ...  # pragma: no cover


@API.experimental
@final
class NeutralWeight(Singleton):
    """
    Simple :py:class:~.lib.interface.PredicateWeight` implementation where the weight always stays
    the same, neutral. All implementations are treated equally.
    """

    @classmethod
    def of_neutral(cls, predicate: Optional[Predicate[Any]]) -> NeutralWeight:
        return cls()

    def __lt__(self, other: NeutralWeight) -> bool:
        return False

    def __add__(self, other: NeutralWeight) -> NeutralWeight:
        return self

    def __str__(self) -> str:
        return "N"


WeightCo = TypeVar('WeightCo', bound=PredicateWeight, covariant=True)


@API.experimental
@runtime_checkable
class Predicate(Protocol[WeightCo]):
    """
    A predicate can be used to define in which conditions an implementations should be used. A
    single method must be implemented :py:meth:`.weight` which should return an optional
    :py:class:~.lib.interface.PredicateWeight`. It is called immediately at import time.
    The weight is used to determine the ordering of the implementations. If :py:obj:`None` is
    returned, the implementation will not be used at all, which allows one to customize which
    implementations are available at import time.

    Antidote only provides a single weight system out of the box,
    :py:class:~.lib.interface.NeutralWeight` which as its name implies does not provide any
    ordering. All implementations are treated equally. You're free to use your own weight though,
    see :py:class:~.lib.interface.PredicateWeight` for more details.

    .. doctest:: lib_interface_predicate

        >>> from typing import Optional
        >>> import os
        >>> from antidote import Constants, const, inject, interface, implements, world
        >>> from antidote.lib.interface import NeutralWeight
        >>> class Conf(Constants):
        ...     CLOUD = const[str]('aws')
        >>> class InCloud:
        ...     def __init__(self, cloud: str) -> None:
        ...         self.cloud = cloud
        ...
        ...     @inject
        ...     def weight(self, cloud: str = Conf.CLOUD) -> Optional[NeutralWeight]:
        ...         if cloud == self.cloud:
        ...             return NeutralWeight()
        >>> @interface
        ... class ObjectStorage:
        ...     def put(self, name: str, data: bytes) -> None:
        ...         pass
        >>> @implements(ObjectStorage).when(InCloud('aws'))
        ... class AwsStorage(ObjectStorage):
        ...     pass
        >>> @implements(ObjectStorage).when(InCloud('gcp'))
        ... class GCPStorage(ObjectStorage):
        ...     pass
        >>> world.get[ObjectStorage].all()
        [<AwsStorage ...>]

    At most one predicate of a specific type can be used on a single implementation. Multiple
    predicates can share mother classes though. However, multiple predicates of a given type can be
    provided to :py:meth:`~.implements.when` if you declare the
    :py:meth:`typeclasses.perdicate.merge` function used to merge them together.


    """

    def weight(self) -> Optional[WeightCo]:
        ...  # pragma: no cover


Pct = TypeVar('Pct', bound=Predicate[Any], contravariant=True)


@API.experimental
@runtime_checkable
class PredicateConstraint(Protocol[Pct]):
    """
    A constraint can be used to define at runtime whether a given predicate matches a specific
    criteria or not. Antidote will evaluate the constraint on all predicate that matches the
    argument type hint. If not predicate of this type is present on an implementation, it is
    evaluated with :py:obj:`None` instead.

    .. doctest:: lib_interface_constraint

        >>> from typing import Optional, Protocol
        >>> from antidote import QualifiedBy, interface, implements, world
        >>> class NotQualified:
        ...     def evaluate(self, predicate: Optional[QualifiedBy]) -> bool:
        ...         return predicate is None
        >>> class AtLeastTwoQualifiers:
        ...     def evaluate(self, predicate: Optional[QualifiedBy]) -> bool:
        ...         return predicate is not None and len(predicate.qualifiers) >= 2
        >>> @interface
        ... class Dummy(Protocol):
        ...     pass
        >>> @implements(Dummy)
        ... class NoQualifiers:
        ...     pass
        >>> @implements(Dummy).when(qualified_by=object())
        ... class OneQualifier:
        ...     pass
        >>> @implements(Dummy).when(qualified_by=[object(), object()])
        ... class TwoQualifiers:
        ...     pass
        >>> world.get[Dummy].single(NotQualified())
        <NoQualifiers ...>
        >>> world.get[Dummy].single(AtLeastTwoQualifiers())
        <TwoQualifiers ...>

    Contrary to :py:class:~.lib.interface.Predicate` you can use multiple instances of a single
    constraint class. But, you can still define a merge function with
    :py:meth:`typeclasses.perdicate.merge_constraint` which is intended for runtime optimization
    if possible.

    """

    def evaluate(self, predicate: Optional[Pct]) -> bool:
        ...  # pragma: no cover


P = TypeVar('P', bound=Predicate[Any])
PC = TypeVar('PC', bound=PredicateConstraint[Any])


@API.experimental  # Prefer using `typeclasses.predicate`
@final
class predicate_typeclasses:
    @staticmethod
    def merge(f: Callable[[P, P], P]) -> Callable[[P, P], P]:
        """
        Decorator to be applied on the function used to merge a certain type of predicates. The
        type is inferred from the type hints.

        ... doctest:: lib_interface_typeclass_merge

            >>> from typing import Optional
            >>> from antidote import typeclasses
            >>> from antidote.lib.interface import NeutralWeight
            >>> class UseMe:
            ...     @staticmethod
            ...     @typeclasses.predicate.merge
            ...     def merge(a: UseMe, b: UseMe) -> UseMe:
            ...         return UseMe(a.condition and b.condition)
            ...
            ...     def __init__(self, condition: bool) -> None:
            ...         self.condition = condition
            ...
            ...     def weight(self) -> Optional[NeutralWeight]:
            ...         return NeutralWeight() if self.condition else None


        """
        from ._internal import register_predicate_merge
        register_predicate_merge(f)
        return f

    @staticmethod
    def merge_constraint(f: Callable[[PC, PC], PC]) -> Callable[[PC, PC], PC]:
        """
        Decorator to be applied on the function used to merge a certain type of predicate
        constraints. The type is inferred from the type hints.

        ... doctest:: lib_interface_typeclass_merge

            >>> from typing import Optional
            >>> from antidote import typeclasses, QualifiedBy
            >>> from antidote.lib.interface import NeutralWeight
            >>> class NotQualified:
            ...     @staticmethod
            ...     @typeclasses.predicate.merge
            ...     def merge(a: NotQualified, b: NotQualified) -> NotQualified:
            ...         return a
            ...
            ...     def evaluate(self, predicate: Optional[QualifiedBy]) -> bool:
            ...         return predicate is None


        """
        from ._internal import register_predicate_constraint_merge
        register_predicate_constraint_merge(f)
        return f
