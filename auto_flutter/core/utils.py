from __future__ import annotations

from abc import ABCMeta
from typing import Callable, Dict, Iterable, List, Optional, Type, TypeVar


class _Iterable(metaclass=ABCMeta):
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


class _Dict(metaclass=ABCMeta):
    K = TypeVar("K")
    V = TypeVar("V")

    def get_or_none(input: Dict[K, V], key: K) -> Optional[V]:
        return None if not key in input else input[key]

    def get_or_default(input: Dict[K, V], key: K, fallback: Callable[[], V]) -> V:
        return fallback() if not key in input else input[key]


class _Ensure(metaclass=ABCMeta):
    T = TypeVar("T")

    def not_none(input: Optional[T], name: Optional[str] = None) -> T:
        if input is None:
            if name is None:
                raise AssertionError("Field require valid value")
            else:
                raise AssertionError("Field `{}` require valid value".format(name))
        return input

    def type(input: Optional[T], cls: Type[T], name: Optional[str] = None):
        if input is None:
            return
        if isinstance(input, cls):
            return
        if name is None:
            raise AssertionError("Field must be instance of `{}`".format(cls.__name__))
        else:
            raise AssertionError(
                "Field `{}` must be instance of `{}`".format(name, cls.__name__)
            )
