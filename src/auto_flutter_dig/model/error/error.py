from __future__ import annotations

from traceback import TracebackException
from typing import Generic, TypeVar

__all__ = ["TaskNotFound", "format_exception"]


class TaskNotFound(LookupError):
    def __init__(self, task_id: str, *args: object) -> None:
        super().__init__(*args)
        self.task_id: str = task_id


def format_exception(error: BaseException) -> str:
    from ...core.config import Config
    from ...module.aflutter.config.const import AFLUTTER_CONFIG_ENABLE_STACK_STRACE

    if Config.get_bool(AFLUTTER_CONFIG_ENABLE_STACK_STRACE):
        return "".join(TracebackException.from_exception(error).format())
    return str(error)
