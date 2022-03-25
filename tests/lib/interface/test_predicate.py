# pyright: reportUnusedClass=false, reportUnusedFunction=false
from typing import Any, Callable, Iterator, TypeVar

import pytest

from antidote import implements, interface, QualifiedBy, typeclasses, world
from antidote._providers import ServiceProvider
from antidote.lib.interface import NeutralWeight, register_interface_provider

T = TypeVar('T')


def _(x: T) -> T:
    return x


@pytest.fixture(autouse=True)
def setup_world() -> Iterator[None]:
    with world.test.empty():
        world.provider(ServiceProvider)
        register_interface_provider()
        yield


def test_neutral_weight() -> None:
    neutral = NeutralWeight()
    assert NeutralWeight() is neutral
    assert (NeutralWeight() + NeutralWeight()) == neutral
    assert not (NeutralWeight() < neutral)


@pytest.mark.parametrize('decorator', [
    pytest.param(typeclasses.predicate.merge, id="merge"),
    pytest.param(typeclasses.predicate.merge_constraint, id="merge_constraint")
])
def test_invalid_predicate_type_class(decorator: Callable[[Any], Any]) -> None:
    with pytest.raises(TypeError, match="(?i).*function.*"):
        decorator(object())

    with pytest.raises(TypeError, match="(?i).*return type hint.*"):
        @decorator
        def f(a, b):  # type: ignore
            pass  # pragma: no cover

    @interface
    class Base:
        pass

    with pytest.raises(RuntimeError, match="(?i).*multiple.*"):
        @decorator
        def f2(a: QualifiedBy, b: QualifiedBy) -> QualifiedBy:
            return a  # pragma: no cover

        # Error should be raised at latest when declaring an implementation
        # or querying it for the predicate constraint
        @_(implements(Base).when(QualifiedBy(object()), QualifiedBy(object())))
        class BaseImpl(Base):
            pass

        world.get[Base].single(QualifiedBy(object()), QualifiedBy(object()))

    with pytest.raises(TypeError, match="(?i).*expected.*Predicate.*int.*"):
        @decorator
        def f3(a, b) -> int:  # type: ignore
            pass  # pragma: no cover

        # Error should be raised at latest when declaring an implementation
        # or querying it for the predicate constraint
        @_(implements(Base).when(QualifiedBy(object()), QualifiedBy(object())))
        class BaseImpl2(Base):
            pass

        world.get[Base].single(QualifiedBy(object()), QualifiedBy(object()))
