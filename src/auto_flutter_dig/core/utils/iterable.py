from __future__ import annotations

from abc import ABC
from typing import (
    Callable,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
)


class _Iterable(ABC):
    T = TypeVar("T")
    T_co = TypeVar("T_co", covariant=True)

    def first_or_none(iterable: Iterable[T], condition: Callable[[T], bool]) -> Optional[T]:
        for it in iterable:
            if condition(it):
                return it
        return None

    def first_or_default(iterable: Iterable[T], condition: Callable[[T], bool], fallback: Callable[[], T]) -> T:
        for it in iterable:
            if condition(it):
                return it
        return fallback()

    def flatten(iterable: Iterable[Iterable[T]]) -> List[T]:
        return [item for sublist in iterable for item in sublist]

    def count(iterable: Iterable[T]) -> int:
        out = 0
        for it in iterable:
            out += 1
        return out

    def is_empty(iterable: Iterable[T]) -> bool:
        for it in iterable:
            return False
        return True

    class not_none(Iterator[T], Generic[T]):
        def __init__(self, iter: Iterable[Optional[_Iterable.T]]) -> None:
            super().__init__()
            self._iter = iter.__iter__()

        def __iter__(self) -> _Iterable.not_none[_Iterable.T]:
            return self

        def __next__(self) -> _Iterable.T:
            while True:
                out = next(self._iter)
                if not out is None:
                    return out

    K = TypeVar("K")

    class tuple_not_none(Iterator[Tuple[K, T]]):
        def __init__(self, iter: Iterable[Tuple[_Iterable.K, Optional[_Iterable.T]]]) -> None:
            super().__init__()
            self._iter = iter.__iter__()

        def __iter__(self) -> _Iterable.tuple_not_none:
            return self

        def __next__(self) -> Tuple[_Iterable.K, _Iterable.T]:
            while True:
                out = next(self._iter)
                if not out[1] is None:
                    return (out[0], out[1])

    class join(Iterator[T]):
        def __init__(self, *iterables: Iterable[_Iterable.T]) -> None:
            super().__init__()
            self.__iterators: List[Iterator[_Iterable.T]] = list(map(lambda x: x.__iter__(), iterables))
            self.__current = 0

        def __iter__(self) -> Iterator[_Iterable.T]:
            return self

        def __next__(self) -> _Iterable.T:
            while self.__current < len(self.__iterators):
                try:
                    item = next(self.__iterators[self.__current])
                except StopIteration:
                    self.__current += 1
                    continue
                return item
            raise StopIteration()

    class modify(Iterator[T_co]):
        def __init__(
            self,
            iterable: Iterable[_Iterable.T_co],
            apply: Callable[[_Iterable.T_co], None],
        ) -> None:
            super().__init__()
            self.__iterator = iterable.__iter__()
            self.__apply = apply

        def __next__(self) -> _Iterable.T_co:
            item = next(self.__iterator)
            self.__apply(item)
            return item

    class is_instance(Iterator[T_co]):
        def __init__(self, iterable: Iterable[_Iterable.T], cls: Type[_Iterable.T_co]) -> None:
            super().__init__()
            self.__iterator = iterable.__iter__()
            self.__cls = cls

        def __next__(self) -> _Iterable.T_co:
            while True:
                out = next(self.__iterator)
                if isinstance(out, self.__cls):
                    return out
