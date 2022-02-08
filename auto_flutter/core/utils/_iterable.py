from abc import ABC
from typing import Callable, Iterable, List, Optional, TypeVar


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
        try:
            next(iterable)
            return False
        except StopIteration:
            pass
        return True
