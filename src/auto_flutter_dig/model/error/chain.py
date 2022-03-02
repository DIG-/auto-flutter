from typing import Generic, TypeVar

T = TypeVar("T", bound=BaseException)


class E(Generic[T]):
    def __init__(self, error: T) -> None:
        self._error = error

    @property
    def error(self) -> T:
        return self._error

    def caused_by(self, error: BaseException) -> T:
        self._error.__cause__ = error
        return self._error
