from abc import ABC
from typing import Callable, Optional, TypeVar

from ._ensure import _Ensure


class _If(ABC):
    T = TypeVar("T")
    V = TypeVar("V")

    @staticmethod
    def none(
        input: Optional[T], positive: Callable[[], V], negative: Callable[[T], V]
    ) -> V:
        _Ensure.instance(positive, Callable, "positive")
        _Ensure.instance(negative, Callable, "negative")
        if input is None:
            return positive()
        return negative(input)

    @staticmethod
    def not_none(
        input: Optional[T], positive: Callable[[T], V], negative: Callable[[], V]
    ) -> V:
        _Ensure.instance(positive, Callable, "positive")
        _Ensure.instance(negative, Callable, "negative")
        if input is None:
            return negative()
        return positive(input)
