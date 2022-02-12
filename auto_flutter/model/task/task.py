from __future__ import annotations

from abc import ABCMeta, abstractclassmethod
from typing import Iterable, List, Union

from ..argument import Args
from .id import TaskId
from .identity import TaskIdentity
from .result import TaskResult

__all__ = ["Task", "List"]


class Task(metaclass=ABCMeta):
    ## Start - Alias to reduce import
    ID = TaskId
    Args = Args
    Result = TaskResult
    Identity = TaskIdentity
    Option = TaskIdentity.Option
    ## End - alias

    identity: Identity = None

    def require(self) -> List[Task.ID]:
        return []

    def describe(self, args: Task.Args) -> str:
        return self.identity.name

    def print(self, message: str):
        from ...core.task.manager import TaskManager

        TaskManager.print(message)

    def _append_task(
        self, tasks: Union[Task, Iterable[Task], Task.Identity, Iterable[Task.Identity]]
    ):
        from ...core.task.manager import TaskManager

        TaskManager.add(tasks)

    def _append_task_id(self, ids: Union[Task.ID, Iterable[Task.ID]]):
        from ...core.task.manager import TaskManager

        TaskManager.add_id(ids)

    @abstractclassmethod
    def execute(self, args: Task.Args) -> Task.Result:
        # Return None when fail
        # Otherwise return given Args with extra args
        raise NotImplementedError
