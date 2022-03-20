from __future__ import annotations

from typing import Iterable, List, Optional, Union

from ...core.task.manager import TaskManager
from ...model.argument.arguments import Args
from ...model.result import Result
from ...model.task.base_task import BaseTask
from ...model.task.id import TaskId
from ...model.task.identity import TaskIdentity
from ...model.task.result import TaskResult

__all__ = ["Task", "Args", "TaskId", "TaskResult", "List"]


class Task(BaseTask):
    def require(self) -> List[TaskId]:
        return []

    def describe(self, args: Args) -> str:
        return self.identity.name

    def _print(self, message: Optional[str]) -> None:
        if message is None:
            return

        TaskManager.print(message)
        self.log.debug(message)

    @staticmethod
    def _uptade_description(
        description: str,
        result: Optional[Result] = None,  # Show some part had failed
    ):
        TaskManager.update_description(description, result)

    def _reset_description(self, args: Args, result: Optional[Result] = None):
        self._uptade_description(self.describe(args), result)

    @staticmethod
    def _append_task(tasks: Union[Task, Iterable[Task], TaskIdentity, Iterable[TaskIdentity]]) -> None:
        TaskManager.add(tasks)

    @staticmethod
    def _append_task_id(ids: Union[TaskId, Iterable[TaskId]]) -> None:
        TaskManager.add_id(ids)
