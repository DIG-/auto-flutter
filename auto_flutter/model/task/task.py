from __future__ import annotations

from abc import ABC, abstractclassmethod, abstractmethod
from typing import Iterable, List, Optional, Union

from ..argument import Args
from .id import TaskId
from .identity import TaskIdentity
from .result import TaskResult

__all__ = ["Task", "List"]


class Task(ABC):
    identity: TaskIdentity

    def require(self) -> List[TaskId]:
        return []

    def describe(self, args: Args) -> str:
        return self.identity.name

    def _print(self, message: Optional[str]) -> None:
        if message is None:
            return
        from ...core.task.manager import TaskManager

        TaskManager.print(message)

    def _append_task(
        self, tasks: Union[Task, Iterable[Task], TaskIdentity, Iterable[TaskIdentity]]
    ) -> None:
        from ...core.task.manager import TaskManager

        TaskManager.add(tasks)

    def _append_task_id(self, ids: Union[TaskId, Iterable[TaskId]]) -> None:
        from ...core.task.manager import TaskManager

        TaskManager.add_id(ids)

    @abstractmethod
    def execute(self, args: Args) -> TaskResult:
        # Return None when fail
        # Otherwise return given Args with extra args
        raise NotImplementedError
