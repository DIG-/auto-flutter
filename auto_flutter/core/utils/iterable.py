from __future__ import annotations

from abc import ABC
from typing import Callable, Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar


class _Iterable(ABC):
    T = TypeVar("T")

    def first_or_none(
        iterable: Iterable[T], condition: Callable[[T], bool]
    ) -> Optional[T]:
        for it in iterable:
            if condition(it):
                return it
        return None

    def first_or_default(
        iterable: Iterable[T], condition: Callable[[T], bool], fallback: Callable[[], T]
    ) -> T:
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
        def __init__(
            self, iter: Iterable[Tuple[_Iterable.K, Optional[_Iterable.T]]]
        ) -> None:
            super().__init__()
            self._iter = iter.__iter__()

        def __iter__(self) -> _Iterable.tuple_not_none:
            return self

        def __next__(self) -> Tuple[_Iterable.K, _Iterable.T]:
            while True:
                out = next(self._iter)
                if not out[1] is None:
                    return (out[0], out[1])
