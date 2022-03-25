from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import cast, Optional, Tuple

from typing_extensions import final

from .predicate import NeutralWeight, predicate_typeclasses, PredicateConstraint
from ..._internal import API

__all__ = ['QualifiedBy']

_BUILTIN_TYPES = cast(Tuple[type, ...], (int, float, str, list, dict, set,
                                         tuple, bytes, bytearray, bool, complex))


@API.public
@final
@dataclass(frozen=True, init=False)
class QualifiedBy:
    __slots__ = ('qualifiers',)
    qualifiers: list[object]

    @classmethod
    def one_of(cls, *qualifiers: object) -> PredicateConstraint[QualifiedBy]:
        return QualifiedByOneOf(QualifiedBy(*qualifiers))

    @classmethod
    def instance_of(cls, klass: type) -> PredicateConstraint[QualifiedBy]:
        return QualifiedByInstanceOf(klass)

    @staticmethod
    @predicate_typeclasses.merge_constraint
    @predicate_typeclasses.merge
    def merge(a: QualifiedBy, b: QualifiedBy) -> QualifiedBy:
        return QualifiedBy(*a.qualifiers, *b.qualifiers)

    def __init__(self, *qualifiers: object):
        if len(qualifiers) == 0:
            raise ValueError("At least one qualifier must be given.")

        for qualifier in qualifiers:
            if qualifier is None or isinstance(qualifier, _BUILTIN_TYPES):
                raise TypeError(f"Invalid qualifier: {qualifier!r}. "
                                f"It cannot be None or an instance of a builtin type")

        object.__setattr__(self, 'qualifiers', [
            next(group)
            for _, group in itertools.groupby(sorted(qualifiers, key=id), key=id)
        ])

    def evaluate(self, predicate: Optional[QualifiedBy]) -> bool:
        if predicate is None:
            return False

        if len(self.qualifiers) > len(predicate.qualifiers):
            return False

        i = 0
        j = 0
        while i < len(self.qualifiers) and j < len(predicate.qualifiers):
            if self.qualifiers[i] is predicate.qualifiers[j]:
                i += 1
                j += 1
            else:
                j += 1

        return i == len(self.qualifiers)

    @staticmethod
    def weight() -> NeutralWeight:
        return NeutralWeight()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QualifiedBy):
            return False

        if len(self.qualifiers) != len(other.qualifiers):
            return False

        for a, b in zip(self.qualifiers, other.qualifiers):
            if a is not b:
                return False

        return True

    def __hash__(self) -> int:
        return hash(tuple(id(q) for q in self.qualifiers))


@API.private  # Use QualifiedBy.one_of
@final
@dataclass(frozen=True, eq=True, unsafe_hash=True)
class QualifiedByOneOf:
    __slots__ = ('__qualified_by',)
    __qualified_by: QualifiedBy

    def evaluate(self, predicate: Optional[QualifiedBy]) -> bool:
        if predicate is None:
            return False

        i = 0
        j = 0
        while i < len(self.__qualified_by.qualifiers) and j < len(predicate.qualifiers):
            idi = id(self.__qualified_by.qualifiers[i])
            idj = id(predicate.qualifiers[j])
            if idi == idj:
                return True
            if idi < idj:
                i += 1
            else:
                j += 1

        return False


@API.private  # Use QualifiedBy.instance_of
@final
@dataclass(frozen=True, eq=True, unsafe_hash=True)
class QualifiedByInstanceOf:
    __slots__ = ('__klass',)
    __klass: type

    def __post_init__(self) -> None:
        if not isinstance(self.__klass, type):
            raise TypeError(f"qualifier_type must be a class, not a {type(self.__klass)}")

    def evaluate(self, predicate: Optional[QualifiedBy]) -> bool:
        if predicate is None:
            return False

        return any(isinstance(qualifier, self.__klass) for qualifier in predicate.qualifiers)
