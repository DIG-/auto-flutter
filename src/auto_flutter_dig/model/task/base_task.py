from abc import ABC, abstractmethod
from logging import LoggerAdapter
from typing import List

from ...core.logger import log_task
from ...model.argument.arguments import Args
from .id import TaskId
from .identity import TaskIdentity
from .result import TaskResult

__all__ = ["BaseTask", "Args", "TaskId", "TaskIdentity", "TaskResult", "List"]


class BaseTask(ABC):
    identity: TaskIdentity

    def __init__(self) -> None:
        self.log = LoggerAdapter(log_task, {"tag": self.__class__.__name__})

    @abstractmethod
    def require(self) -> List[TaskId]:
        raise NotImplementedError(f"{type(self).__name__} must not call super")

    @abstractmethod
    def describe(self, args: Args) -> str:
        raise NotImplementedError(f"{type(self).__name__} must not call super")

    @abstractmethod
    def execute(self, args: Args) -> TaskResult:
        raise NotImplementedError(f"{type(self).__name__} must not call super")
