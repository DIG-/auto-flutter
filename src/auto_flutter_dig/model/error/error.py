from __future__ import annotations

from traceback import TracebackException
from typing import Generic, TypeVar

__all__ = ["TaskNotFound", "E", "format_exception"]


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


def format_exception(error: BaseException) -> str:
    from ...core.config import Config
    from ...module.aflutter.config.const import AFLUTTER_CONFIG_ENABLE_STACK_STRACE

    if Config.get_bool(AFLUTTER_CONFIG_ENABLE_STACK_STRACE):
        return "".join(TracebackException.from_exception(error).format())
    return str(error)
