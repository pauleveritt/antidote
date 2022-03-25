from typing import Any, Optional, Union

import pytest

from antidote.lib.interface import Predicate, QualifiedBy
from antidote.lib.interface._internal import create_constraints as create

x = object()
y = object()


def test_create_constraints_qualifiers() -> None:
    assert create(QualifiedBy(x)) == create(qualified_by=[x])
    assert create(QualifiedBy(x)) == create(qualified_by=x)
    assert create(QualifiedBy(x, y)) == create(qualified_by=[x, y])
    assert create(QualifiedBy.one_of(x)) == create(qualified_by_one_of=[x])
    assert create(QualifiedBy.one_of(x, y)) == create(qualified_by_one_of=[x, y])
    assert create(QualifiedBy.instance_of(int)) == create(qualified_by_instance_of=int)

    assert create(QualifiedBy(x)) == [(QualifiedBy, QualifiedBy(x))]
    assert create(QualifiedBy.one_of(x)) == [(QualifiedBy, QualifiedBy.one_of(x))]
    assert create(QualifiedBy.instance_of(int)) == [(QualifiedBy, QualifiedBy.instance_of(int))]


def test_create_invalid_kwargs() -> None:
    with pytest.raises(TypeError, match="(?i).*Invalid qualifier.*"):
        create(qualified_by=tuple())

    with pytest.raises(TypeError, match="(?i).*qualified_by_one_of.*"):
        create(qualified_by_one_of=tuple())  # type: ignore

    with pytest.raises(TypeError, match="(?i).*Invalid qualifier.*"):
        create(qualified_by_one_of=[tuple()])

    with pytest.raises(TypeError, match="(?i).*type.*"):
        create(qualified_by_instance_of=object())  # type: ignore


def test_create_constraint_combination() -> None:
    assert create(QualifiedBy(x), QualifiedBy(x)) == create(QualifiedBy(x))
    assert create(QualifiedBy(x), QualifiedBy(y)) == create(QualifiedBy(x, y))
    assert set(create(QualifiedBy.one_of(x), QualifiedBy.one_of(y))) == {
        (QualifiedBy, QualifiedBy.one_of(x)),
        (QualifiedBy, QualifiedBy.one_of(y))
    }


def test_create_constraint_invalid_predicate_class() -> None:
    with pytest.raises(TypeError, match="(?i).*PredicateConstraint.*"):
        create(object())  # type: ignore

    class MissingPredicateArgument:
        def evaluate(self, *args: object, **kwargs: object) -> None:
            pass  # pragma: no cover

    with pytest.raises(TypeError, match="(?i).*predicate.*"):
        create(MissingPredicateArgument())  # type: ignore


@pytest.mark.parametrize('type_hint', [
    Any,
    Union[int, float],
    Optional[int],
    Union[None, Predicate[Any], int],
    Predicate[Any]
])
def test_create_constraint_invalid_type_hint(type_hint: Any) -> None:
    class InvalidTypeHint:
        def evaluate(self, predicate: type_hint) -> None:  # type: ignore
            pass  # pragma: no cover

    with pytest.raises(TypeError, match="(?i).*Optional.*Predicate.*"):
        create(InvalidTypeHint())  # type: ignore
