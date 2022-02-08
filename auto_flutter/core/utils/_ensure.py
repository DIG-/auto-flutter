from abc import ABC
from email import message
from typing import Any, Final, Optional, Type, TypeVar


class _Ensure(ABC):
    T = TypeVar("T")

    @staticmethod
    def not_none(input: Optional[T], name: Optional[str] = None) -> T:
        if not input is None:
            return input
        if name is None:
            raise AssertionError("Field require valid value")
        else:
            raise AssertionError("Field `{}` require valid value".format(name))

    @staticmethod
    def type(
        input: Optional[T], cls: Type[T], name: Optional[str] = None
    ) -> Optional[T]:
        if input is None:
            return None
        if isinstance(input, cls):
            return input
        message: Final = (
            "Field must be instance of `{cls}`, but `{input}` was used"
            if name is None
            else "Field `{name}` must be instance of `{cls}`, but `{input}` was used"
        )
        raise TypeError(message.format(name=name, cls=cls.__name__, input=type(input)))

    @staticmethod
    def instance(input: Any, cls: Type[T], name: Optional[str] = None) -> T:
        if not input is None and isinstance(input, cls):
            return input
        message: Final = (
            "Field must be instance of `{cls}`, but `{input}` was used"
            if name is None
            else "Field `{name}` must be instance of `{cls}`, but `{input}` was used"
        )
        raise TypeError(message.format(name=name, cls=cls.__name__, input=type(input)))
