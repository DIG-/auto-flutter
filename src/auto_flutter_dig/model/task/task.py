from __future__ import annotations

from abc import ABC, abstractmethod
from logging import LoggerAdapter
from typing import Iterable, List, Optional, Union

from ...model.error.chain import E
from ...model.result import Result
from ..argument import Args
from .id import TaskId
from .identity import TaskIdentity
from .result import TaskResult

__all__ = ["Task", "List", "E"]


class Task(ABC):
    identity: TaskIdentity

    def __init__(self) -> None:
        super().__init__()
        from ...core.logger import log_task

        self.log = LoggerAdapter(log_task, {"tag": self.__class__.__name__})

    def require(self) -> List[TaskId]:
        return []

    def describe(self, args: Args) -> str:
        return self.identity.name

    def _print(self, message: Optional[str]) -> None:
        if message is None:
            return
        from ...core.task.manager import TaskManager

        TaskManager.print(message)
        self.log.debug(message)

    def _uptade_description(
        self,
        description: str,
        result: Optional[Result] = None,  # Show some part had failed
    ):
        from ...core.task.manager import TaskManager

        TaskManager.update_description(description, result)

    def _reset_description(self, args: Args, result: Optional[Result] = None):
        self._uptade_description(self.describe(args), result)

    def _append_task(self, tasks: Union[Task, Iterable[Task], TaskIdentity, Iterable[TaskIdentity]]) -> None:
        from ...core.task.manager import TaskManager

        TaskManager.add(tasks)

    def _append_task_id(self, ids: Union[TaskId, Iterable[TaskId]]) -> None:
        from ...core.task.manager import TaskManager

        TaskManager.add_id(ids)

    @abstractmethod
    def execute(self, args: Args) -> TaskResult:
        # Return None when fail
        # Otherwise return given Args with extra args
        raise NotImplementedError()
