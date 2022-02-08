from __future__ import annotations

from abc import ABC, ABCMeta
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NoReturn,
    Optional,
    Type,
    TypeVar,
    overload,
)


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


class _Dict(metaclass=ABCMeta):
    K = TypeVar("K")
    V = TypeVar("V")

    def get_or_none(input: Dict[K, V], key: K) -> Optional[V]:
        return None if not key in input else input[key]

    def get_or_default(input: Dict[K, V], key: K, fallback: Callable[[], V]) -> V:
        return fallback() if not key in input else input[key]

    def merge(a: Dict[K, V], b: Optional[Dict[K, V]]) -> Dict[K, V]:
        if b is None:
            return a
        c = a.copy()
        for k, v in b.items():
            c[k] = v
        return c

    def merge_append(
        a: Dict[K, List[V]], b: Optional[Dict[K, List[V]]]
    ) -> Dict[K, List[V]]:
        if b is None:
            return a
        c = a.copy()
        for k, v in b.items():
            if k in c:
                c[k].extend(v)
            else:
                c[k] = v
        return c


class _Raise:
    def __new__(cls: type[_Raise], error: BaseException) -> NoReturn:
        raise error


class _If(ABC):
    T = TypeVar("T")
    V = TypeVar("V")

    @staticmethod
    def none(
        input: Optional[T], positive: Callable[[], V], negative: Callable[[T], V]
    ) -> V:
        _Ensure.type_not_none(positive, Callable, "positive")
        _Ensure.type_not_none(negative, Callable, "negative")
        if input is None:
            return positive()
        return negative(input)

    @overload
    @staticmethod
    def none(input: Optional[T], positive: Callable[[], T]) -> T:
        _Ensure.type_not_none(positive, Callable, "positive")
        if input is None:
            return positive()
        return input

    @staticmethod
    def not_none(
        input: Optional[T], positive: Callable[[T], V], negative: Callable[[], V]
    ) -> V:
        _Ensure.type_not_none(positive, Callable, "positive")
        _Ensure.type_not_none(negative, Callable, "negative")
        if input is None:
            return negative()
        return positive(input)


class _Ensure(metaclass=ABCMeta):
    T = TypeVar("T")

    def not_none(input: Optional[T], name: Optional[str] = None) -> T:
        if input is None:
            if name is None:
                raise AssertionError("Field require valid value")
            else:
                raise AssertionError("Field `{}` require valid value".format(name))
        return input

    def type(
        input: Optional[T], cls: Type[T], name: Optional[str] = None
    ) -> Optional[T]:
        if input is None:
            return None
        if isinstance(input, cls):
            return input
        if name is None:
            raise AssertionError(
                "Field must be instance of `{}`, but `{}` was used".format(
                    cls.__name__, type(input)
                )
            )
        else:
            raise AssertionError(
                "Field `{}` must be instance of `{}`, but `{}` was used".format(
                    name, cls.__name__, type(input)
                )
            )

    def type_not_none(
        input: Optional[T], cls: Type[T], name: Optional[str] = None
    ) -> T:
        if not input is None and isinstance(input, cls):
            return input
        if name is None:
            raise AssertionError(
                "Field must be instance of `{}`, but `{}` was used".format(
                    cls.__name__, type(input)
                )
            )
        else:
            raise AssertionError(
                "Field `{}` must be instance of `{}`, but `{}` was used".format(
                    name, cls.__name__, type(input)
                )
            )

    def instance(input: Any, cls: Type[T], name: Optional[str] = None) -> T:
        if not input is None and isinstance(input, cls):
            return input
        if name is None:
            raise AssertionError(
                "Field must be intance of `{}`, but `{}` was used".format(
                    cls.__name__, type(input)
                )
            )
        else:
            raise AssertionError(
                "Field {} must be intance of `{}`, but `{}` was used".format(
                    name, cls.__name__, type(input)
                )
            )
