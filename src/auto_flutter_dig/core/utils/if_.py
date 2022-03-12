from abc import ABC
from typing import Callable, Optional, TypeVar

from .ensure import _EnsureCallable


class _If(ABC):
    T = TypeVar("T")
    V = TypeVar("V")

    @staticmethod
    def none(input: Optional[T], positive: Callable[[], V], negative: Callable[[T], V]) -> V:
        _EnsureCallable.instance(positive, "positive")
        _EnsureCallable.instance(negative, "negative")

        if input is None:
            return positive()
        return negative(input)

    @staticmethod
    def not_none(input: Optional[T], positive: Callable[[T], V], negative: Callable[[], V]) -> V:
        _EnsureCallable.instance(positive, "positive")
        _EnsureCallable.instance(negative, "negative")

        if input is None:
            return negative()
        return positive(input)
