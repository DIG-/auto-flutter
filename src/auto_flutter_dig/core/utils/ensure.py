from abc import ABC
from types import FunctionType, MethodType
from typing import Any, Callable, NoReturn, Optional, Tuple, Type, TypeVar, Union


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
        input: Optional[T],
        cls: Union[Type[T], Tuple[Type, ...]],
        name: Optional[str] = None,
    ) -> Optional[T]:
        if input is None:
            return None
        if isinstance(input, cls):
            return input
        return _Ensure._raise_error_instance(name, cls, type(input))

    @staticmethod
    def type_returned(
        input: Optional[T],
        cls: Union[Type[T], Tuple[Type, ...]],
        name: Optional[str] = None,
    ) -> Optional[T]:
        if input is None:
            return None
        if isinstance(input, cls):
            return input
        return _Ensure._raise_error_value(name, cls, type(input))

    @staticmethod
    def instance(input: Any, cls: Type[T], name: Optional[str] = None) -> T:
        if not input is None and isinstance(input, cls):
            return input
        return _Ensure._raise_error_instance(name, cls, type(input))

    @staticmethod
    def _raise_error_value(name: Optional[str], cls: Union[T, Type[T], Type], input: Type) -> NoReturn:
        if name is None:
            _Ensure._raise_error(
                "Value must be instance of `{cls}`, but `{input}` was returned",
                "",
                cls,
                input,
            )
        else:
            _Ensure._raise_error(
                "`{name}` must be instance of `{cls}`, but `{input}` was returned",
                name,
                cls,
                input,
            )

    @staticmethod
    def _raise_error_instance(name: Optional[str], cls: Union[T, Type[T], Type], input: Type) -> NoReturn:
        if name is None:
            _Ensure._raise_error(
                "Field must be instance of `{cls}`, but `{input}` was used",
                "",
                cls,
                input,
            )
        else:
            _Ensure._raise_error(
                "Field `{name}` must be instance of `{cls}`, but `{input}` was used",
                name,
                cls,
                input,
            )

    @staticmethod
    def _raise_error(message: str, name: str, cls: Union[T, Type[T], Type], input: Type) -> NoReturn:
        raise TypeError(message.format(name=name, cls=_Ensure.name(cls), input=_Ensure.name(input)))

    @staticmethod
    def name(cls: Union[T, Type[T], Type]) -> str:
        if hasattr(cls, "__name__"):
            return cls.__name__  # type: ignore
        return str(cls)


class _EnsureCallable(ABC):
    T = TypeVar("T", bound=Callable)

    @staticmethod
    def type(
        input: Optional[T],
        name: Optional[str] = None,
    ) -> Optional[T]:
        if input is None:
            return None
        if isinstance(input, (FunctionType, MethodType)):
            return input  # type: ignore
        return _Ensure._raise_error_instance(name, Callable, type(input))

    @staticmethod
    def type_returned(
        input: Optional[T],
        name: Optional[str] = None,
    ) -> Optional[T]:
        if input is None:
            return None
        if isinstance(input, (FunctionType, MethodType)):
            return input  # type: ignore
        return _Ensure._raise_error_value(name, Callable, type(input))

    @staticmethod
    def instance(input: Optional[T], name: Optional[str] = None) -> T:
        if not input is None and isinstance(input, (FunctionType, MethodType)):
            return input  # type: ignore
        return _Ensure._raise_error_instance(name, Callable, type(input))
