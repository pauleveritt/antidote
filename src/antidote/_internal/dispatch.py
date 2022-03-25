import threading
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Deque, Dict, Generic, Optional, Tuple, TypeVar

from typing_extensions import final

from . import API

C = TypeVar('C', bound=type)
F = TypeVar('F', bound=Callable[..., Any])


@API.private
@final
@dataclass(frozen=True)
class LazyDispatch(Generic[C, F]):
    name: str
    __functions: Dict[C, F] = field(default_factory=dict)
    __lazy_registrations: Deque[Tuple[Callable[[F], C], F]] = field(default_factory=deque)
    __lock: threading.Lock = field(default_factory=threading.Lock)

    def register(self,
                 key: Callable[[F], C],
                 func: F) -> None:
        with self.__lock:
            self.__lazy_registrations.append((key, func))

    def get(self, item: C) -> Optional[F]:
        with self.__lock:
            while self.__lazy_registrations:
                key, func = self.__lazy_registrations.pop()
                tpe = key(func)
                previous = self.__functions.get(tpe)
                if previous is not None:
                    raise RuntimeError(
                        f"Multiple implementation of {self.name} declared for {tpe}: "
                        f"{func} and {previous}")
                self.__functions[key(func)] = func

        return self.__functions.get(item)
