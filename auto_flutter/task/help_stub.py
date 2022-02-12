from typing import Optional, Union

from ..model.task import Task


class HelpStub(Task):
    def __init__(
        self,
        task_id: Optional[Union[Task.ID, Task.Identity]] = None,
        message: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._task_id = task_id
        self._message = message
        pass

    def describe(self, args: Task.Args) -> str:
        return ""

    def execute(self, args: Task.Args) -> Task.Result:
        from .help import Help

        self._append_task(Help(self._task_id, self._message))
        return Task.Result(args)
