from __future__ import annotations

from abc import ABCMeta, abstractclassmethod
from typing import Iterable, List, Union

from ..argument import Args
from .id import TaskId
from .identity import Option, TaskIdentity
from .result import TaskResult

__all__ = ["Task", "List"]


class Task(metaclass=ABCMeta):
    ## Start - Alias to reduce import
    ID = TaskId
    Args = Args
    Result = TaskResult
    Identity = TaskIdentity
    Option = Option
    ## End - alias

    identity: TaskIdentity

    def require(self) -> List[TaskId]:
        return []

    def describe(self, args: Args) -> str:
        return self.identity.name

    def _print(self, message: str) -> None:
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

    @abstractclassmethod
    def execute(self, args: Args) -> TaskResult:
        # Return None when fail
        # Otherwise return given Args with extra args
        raise NotImplementedError
