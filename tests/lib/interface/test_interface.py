# pyright: reportUnusedClass=false
from __future__ import annotations

from typing import Any, Iterable, Iterator, List, Optional, Sequence, TypeVar

import sys
import pytest
from typing_extensions import Protocol, runtime_checkable

from antidote import ImplementationsOf, implements, inject, interface, service, world
from antidote._internal.world import WorldGet
from antidote._providers import ServiceProvider
from antidote.core.exceptions import DependencyInstantiationError, DependencyNotFoundError
from antidote.lib.interface import QualifiedBy, register_interface_provider

T = TypeVar('T')


def _(x: T) -> T:
    return x


class Base:
    pass


class Qualifier:
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f"Qualifier({self.name})"


class SubQualifier(Qualifier):
    pass


qA = Qualifier("qA")
qB = Qualifier("qB")
sqC = SubQualifier("qC")
qD = Qualifier("qD")


@pytest.fixture(params=['typed_get', 'interface', 'inject'])
def get(request: Any) -> WorldGet:
    if request.param == 'typed_get':
        return world.get
    elif request.param == "interface":
        class Query:
            def __init__(self, interface: type) -> None:
                self.interface = interface

            def single(self, *args: Any, **kwargs: Any) -> Any:
                return world.get(ImplementationsOf[object](self.interface).single(*args, **kwargs))

            def all(self, *args: Any, **kwargs: Any) -> Any:
                return world.get(ImplementationsOf[object](self.interface).all(*args, **kwargs))

        class Getter:
            def __getitem__(self, interface: type) -> Query:
                return Query(interface)

        return Getter()  # type: ignore
    else:
        class FromInject:
            def __init__(self, interface: type) -> None:
                self.interface = interface

            def single(self, *args: Any, **kwargs: Any) -> Any:
                def f(x: object = inject.impl(*args, **kwargs)) -> object:
                    return x

                f.__annotations__ = {'x': self.interface}
                return inject(f)()

            def all(self, *args: Any, **kwargs: Any) -> Any:
                def f(x: object = inject.impl(*args, **kwargs)) -> object:
                    return x

                f.__annotations__ = {'x': List[self.interface]}  # type: ignore
                return inject(f)()

        class GetterInject:
            def __getitem__(self, interface: type) -> FromInject:
                return FromInject(interface)

        return GetterInject()  # type: ignore


@pytest.fixture(autouse=True)
def setup_world() -> Iterator[None]:
    with world.test.empty():
        world.provider(ServiceProvider)
        register_interface_provider()
        yield


def test_single_implementation() -> None:
    interface(Base)

    @implements(Base)
    class Dummy(Base):
        pass

    # Dummy declared as a singleton
    dummy = world.get(Dummy)
    assert isinstance(dummy, Dummy)
    assert dummy is world.get(Dummy)

    # Base is implemented by Dummy
    with pytest.raises(DependencyNotFoundError):
        world.get(Base)

    with pytest.raises(DependencyNotFoundError):
        world.get[object](ImplementationsOf(Base))

    assert world.get(ImplementationsOf(Base).single()) is dummy
    assert world.get[Base].single() is dummy

    bases: Sequence[object] = world.get(ImplementationsOf(Base).all())
    assert isinstance(bases, list)
    assert len(bases) == 1
    assert bases[0] is dummy

    assert world.get[Base].all() == bases

    @inject
    def single_base(x: Base = inject.impl()) -> Base:
        return x

    assert single_base() is dummy

    @inject
    def all_bases(x: List[Base] = inject.impl()) -> List[Base]:
        return x

    bases = all_bases()
    assert isinstance(bases, list)
    assert len(bases) == 1
    assert bases[0] is dummy

    if sys.version_info >= (3, 9):
        @inject
        def all_bases_type_alias(x: list[Base] = inject.impl()) -> List[Base]:
            return x

        assert all_bases_type_alias() == all_bases()

    @inject
    def all_bases_sequence(x: Sequence[Base] = inject.impl()) -> Sequence[Base]:
        return x

    assert all_bases_sequence() == all_bases()

    @inject
    def all_bases_iterable(x: Iterable[Base] = inject.impl()) -> Iterable[Base]:
        return x

    assert all_bases_iterable() == all_bases()


def test_qualified_implementations(get: WorldGet) -> None:
    interface(Base)

    @_(implements(Base).when(qualified_by=qA))
    class A(Base):
        pass

    @_(implements(Base).when(qualified_by=qB))
    class B(Base):
        pass

    @_(implements(Base).when(qualified_by=[sqC]))
    class C(Base):
        pass

    @_(implements(Base).when(qualified_by=[sqC, qD]))
    class CD(Base):
        pass

    @_(implements(Base))
    class Void(Base):
        pass

    with pytest.raises(DependencyNotFoundError):
        world.get(Base)

    with pytest.raises(DependencyNotFoundError):
        world.get[Base]()

    with pytest.raises(DependencyNotFoundError):
        world.get[object](ImplementationsOf(Base))

    with pytest.raises(DependencyInstantiationError):
        get[Base].single()

    a = world.get(A)
    b = world.get(B)
    c = world.get(C)
    cd = world.get(CD)
    void = world.get(Void)

    # qualified_by
    assert get[Base].single(qualified_by=[qA]) is a
    assert get[Base].single(qualified_by=[qB]) is b

    assert set(get[Base].all()) == {a, b, c, cd, void}
    assert get[Base].all(qualified_by=[qA]) == [a]
    assert get[Base].all(qualified_by=[qB]) == [b]

    # qualified_b // impossible
    with pytest.raises(DependencyNotFoundError):
        get[Base].single(qualified_by=[qA, qB])

    assert set(get[Base].all(qualified_by=[qA, qB])) == set()

    # qualified_by // multiple
    assert get[Base].single(qualified_by=[sqC, qD]) is cd
    assert get[Base].all(qualified_by=[sqC, qD]) == [cd]

    # qualified_by_one_of
    assert get[Base].single(qualified_by_one_of=[qD]) is cd
    assert get[Base].all(qualified_by_one_of=[qD]) == [cd]

    with pytest.raises(DependencyInstantiationError):
        get[Base].single(qualified_by_one_of=[sqC])

    with pytest.raises(DependencyInstantiationError):
        get[Base].single(qualified_by_one_of=[qA, qB])

    assert set(get[Base].all(qualified_by_one_of=[sqC])) == {c, cd}
    assert set(get[Base].all(qualified_by_one_of=[qA, qB])) == {a, b}

    # qualified_by_instance_of
    with pytest.raises(DependencyInstantiationError):
        get[Base].single(qualified_by_instance_of=SubQualifier)

    assert set(get[Base].all(qualified_by_instance_of=SubQualifier)) == {c, cd}
    assert set(get[Base].all(qualified_by_instance_of=Qualifier)) == {a, b, c, cd}

    # Constraints
    assert get[Base].single(QualifiedBy(qA)) is a
    assert get[Base].all(QualifiedBy(qA)) == [a]
    assert get[Base].single(QualifiedBy.one_of(qD)) is cd
    assert set(get[Base].all(QualifiedBy.one_of(sqC))) == {c, cd}
    assert set(get[Base].all(QualifiedBy.instance_of(SubQualifier))) == {c, cd}

    # Mixed constraints
    assert get[Base].single(QualifiedBy.one_of(qD), QualifiedBy.instance_of(SubQualifier)) is cd
    assert get[Base].all(QualifiedBy.one_of(qD), QualifiedBy.instance_of(SubQualifier)) == [cd]
    assert get[Base].single(QualifiedBy.one_of(qD), QualifiedBy.one_of(sqC)) is cd
    assert get[Base].all(QualifiedBy.one_of(qD), QualifiedBy.one_of(sqC)) == [cd]


def test_invalid_interface() -> None:
    with pytest.raises(TypeError, match="(?i).*class.*"):
        interface(object())  # type: ignore

    with pytest.raises(TypeError, match="(?i).*class.*"):
        ImplementationsOf(object())  # type: ignore

    with pytest.raises(ValueError, match="(?i).*decorated.*@interface.*"):
        ImplementationsOf(Qualifier)


def test_invalid_implementation() -> None:
    interface(Base)

    class BaseImpl(Base):
        pass

    with pytest.raises(TypeError, match="(?i).*class.*implementation.*"):
        implements(Base)(object())  # type: ignore

    with pytest.raises(TypeError, match="(?i).*class.*interface.*"):
        implements(object())(BaseImpl)  # type: ignore

    with pytest.raises(TypeError, match="(?i).*instance.*Predicate.*"):
        implements(Base).when(object())(BaseImpl)  # type: ignore

    # should work
    implements(Base)(BaseImpl)


def test_unique_predicate() -> None:
    interface(Base)

    class MyPred:
        def weight(self) -> Optional[Any]:
            return None

    with pytest.raises(RuntimeError, match="(?i).*unique.*"):
        @_(implements(Base).when(MyPred(), MyPred()))
        class BaseImpl(Base):
            pass

    # should work
    @_(implements(Base).when(MyPred()))
    class BaseImplV2(Base):
        pass


def test_custom_service() -> None:
    interface(Base)

    @implements(Base)
    @service(singleton=False)
    class BaseImpl(Base):
        pass

    # is a singleton
    assert world.get(BaseImpl) is not world.get(BaseImpl)
    assert isinstance(world.get[Base].single(), BaseImpl)


def test_type_enforcement_if_possible() -> None:
    interface(Base)

    with pytest.raises(TypeError, match="(?i).*subclass.*Base.*"):
        @implements(Base)
        class Invalid1:
            pass

    @interface
    class BaseProtocol(Protocol):
        def method(self) -> None:
            pass  # pragma: no cover

    @implements(BaseProtocol)
    class Invalid2:
        pass

    @interface
    @runtime_checkable
    class RuntimeProtocol(Protocol):
        def method(self) -> None:
            pass  # pragma: no cover

    with pytest.raises(TypeError, match="(?i).*protocol.*RuntimeProtocol.*"):
        @implements(RuntimeProtocol)
        class Invalid3:
            pass
