from typing import Iterator, Optional

import pytest

from antidote import factory, inject, service, world
from antidote.core.marker import Marker
from antidote.exceptions import DependencyNotFoundError


@pytest.fixture(autouse=True)
def setup_world() -> Iterator[None]:
    with world.test.new():
        yield


def test_marker_me():
    @service
    class MyService:
        pass

    @inject
    def f(my_service: MyService = inject.me()):
        return my_service

    assert f() is world.get[MyService]()


def test_invalid_marker_me_missing_dependency():
    class MyService:
        pass

    @inject
    def f(my_service: MyService = inject.me()):
        return my_service

    # Should not fail before.
    with pytest.raises(DependencyNotFoundError):
        f()


def test_invalid_marker_me_wrong_type_hint():
    with pytest.raises(TypeError, match=r"(?i).*inject\.me.*"):
        @inject
        def f(my_service=inject.me()):
            return my_service

    with pytest.raises(TypeError, match=r"(?i).*inject\.me.*"):
        @inject
        def g(my_service: int = inject.me()):
            return my_service


def test_marker_me_from():
    class MyService:
        pass

    @factory
    def create_service() -> MyService:
        return MyService()

    @inject
    def f(my_service: MyService = inject.me(source=create_service)):
        return my_service

    assert f() is world.get(MyService, source=create_service)


def test_invalid_marker_me_from_wrong_type_hint():
    class MyService:
        pass

    @factory
    def create_service() -> MyService:
        return MyService()

    with pytest.raises(TypeError, match=r"(?i).*inject\.me.*"):
        @inject
        def f(my_service=inject.me(source=create_service)):
            return my_service

    with pytest.raises(TypeError, match=r"(?i).*inject\.me.*"):
        @inject
        def g(my_service: int = inject.me(source=create_service)):
            return my_service

    class OtherService:
        pass

    with pytest.raises(TypeError, match=r"(?i).*does not match.*"):
        @inject
        def h(my_service: OtherService = inject.me(source=create_service)):
            return my_service


def test_marker_get():
    @service
    class MyService:
        pass

    @inject
    def f(my_service=inject.get(MyService)):
        return my_service

    assert f() is world.get[MyService]()


def test_invalid_marker_get_missing_dependency():
    class MyService:
        pass

    @inject
    def f(my_service=inject.get(MyService)):
        return my_service

    # Should not fail before.
    with pytest.raises(DependencyNotFoundError):
        f()


def test_marker_from_get():
    class MyService:
        pass

    @factory
    def create_service() -> MyService:
        return MyService()

    @inject
    def f(my_service=inject.get(MyService, source=create_service)):
        return my_service

    assert f() is world.get(MyService, source=create_service)


def test_invalid_marker_from_get_wrong_target():
    class MyService:
        pass

    @factory
    def create_service() -> MyService:
        return MyService()

    class OtherService:
        pass

    with pytest.raises(TypeError, match=r"(?i).*does not match.*"):
        @inject
        def f(my_service: OtherService = inject.me(source=create_service)):
            return my_service


def test_custom_marker():
    class CustomMarker(Marker):
        pass

    with pytest.raises(TypeError, match="(?i).*custom marker.*"):
        @inject
        def test(test=CustomMarker()):
            pass


def test_marker_me_optional():
    @service
    class MyService:
        pass

    @inject
    def f(my_service: Optional[MyService] = inject.me()):
        return my_service

    assert f() is world.get[MyService]()

    with world.test.empty():
        assert f() is None


def test_marker_me_optional_source():
    class MyService:
        pass

    @factory
    def create_service() -> MyService:
        return MyService()

    @inject
    def f(my_service: Optional[MyService] = inject.me(source=create_service)):
        return my_service

    assert f() is world.get(MyService, source=create_service)

    with world.test.empty():
        assert f() is None
