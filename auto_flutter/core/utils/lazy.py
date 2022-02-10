from __future__ import annotations

from abc import abstractclassmethod
from typing import Callable, Generic, Optional, TypeVar

T = TypeVar("T")


class _Gettable(Generic[T]):
    @abstractclassmethod
    def get(self) -> T:
        raise NotImplementedError()

    def __get(self) -> T:
        return self.get()

    value: T = property(__get)


class _NotLazy(_Gettable[T]):
    def __init__(self, item: T) -> None:
        super().__init__()
        self.__item: T = item

    def get(self) -> T:
        return self.__item


class _Lazy(_Gettable[T]):
    def __init__(self, creator: Callable[[], T]) -> None:
        super().__init__()
        self.__creator: Callable[[], T] = creator
        self.__item: Optional[T] = None

    def get(self) -> T:
        if self.__item is None:
            self.__item = self.__creator()
        return self.__item


class _Dynamically(_Gettable[T]):
    def __init__(self, creator: Callable[[], T]) -> None:
        super().__init__()
        self.__creator: Callable[[], T] = creator

    def get(self) -> T:
        return self.__creator()
