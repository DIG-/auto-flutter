from sys import _getframe as sys_getframe
from types import TracebackType
from typing import Generic, TypeVar

T = TypeVar("T", bound=BaseException)


class E(Generic[T]):
    def __init__(self, error: T) -> None:
        self.__error = error

    @property
    def error(self) -> T:
        return self.__with_traceback(self.__error)

    def caused_by(self, error: BaseException) -> T:
        self.__error.__cause__ = error
        return self.__with_traceback(self.__error)

    def __with_traceback(self, error: T) -> T:
        if error.__traceback__ is None:
            frame = sys_getframe(2)
            error.__traceback__ = TracebackType(None, frame, frame.f_lasti, frame.f_lineno)
        return error
