from typing import Optional, Union

from ..model.task import *


class HelpStub(Task):
    def __init__(
        self,
        task_id: Optional[Union[TaskId, TaskIdentity]] = None,
        message: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._task_id = task_id
        self._message = message
        pass

    def describe(self, args: Args) -> str:
        return ""

    def execute(self, args: Args) -> TaskResult:
        from .help import Help

        self._append_task(Help(self._task_id, self._message))
        return TaskResult(args)
