from __future__ import annotations

from abc import ABCMeta, abstractclassmethod
from typing import List

from ..argument import Args
from . import TaskId, TaskIdentity, TaskResult


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
        from ...core.task_manager import TaskManager

        TaskManager.instance().print(message)

    @abstractclassmethod
    def execute(self, args: Task.Args) -> Task.Result:
        # Return None when fail
        # Otherwise return given Args with extra args
        raise NotImplementedError
