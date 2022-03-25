from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional, Type, TYPE_CHECKING, TypeVar, Union

from typing_extensions import final

from .._internal import API

if TYPE_CHECKING:
    from .typing import CallableClass, Source

T = TypeVar('T')


@API.private
class Marker:
    pass


@API.private  # See @inject decorator for usage.
@final
@dataclass(frozen=True)
class InjectMeMarker(Marker):
    __slots__ = ('source',)
    source: Optional[Union[Source[Any], Callable[..., Any], Type[CallableClass[Any]]]]


@API.private
@final
@dataclass(frozen=True)
class InjectImplMarker(Marker):
    __slots__ = ('constraints_args', 'constraints_kwargs')
    constraints_args: tuple[Any, ...]
    constraints_kwargs: dict[str, Any]
