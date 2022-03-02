from __future__ import annotations

from traceback import TracebackException
from typing import Generic, TypeVar

__all__ = ["TaskNotFound"]


class TaskNotFound(LookupError):
    def __init__(self, task_id: str, *args: object) -> None:
        super().__init__(*args)
        self.task_id: str = task_id
