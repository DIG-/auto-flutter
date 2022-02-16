from __future__ import annotations

from typing import Generic, TypeVar

__all__ = ["SilentWarning", "TaskNotFound", "E"]


class SilentWarning(Warning):
    ...


class TaskNotFound(LookupError):
    def __init__(self, task_id: str, *args: object) -> None:
        super().__init__(*args)
        self.task_id: str = task_id


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
