from typing import Union

from ..model.task import Task


class HelpStub(Task):
    def __init__(self, task_id: Union[Task.ID, Task.Identity]) -> None:
        super().__init__()
        self._task_id = task_id
        pass

    def describe(self, args: Task.Args) -> str:
        return ""

    def execute(self, args: Task.Args) -> Task.Result:
        from .help import Help

        self._append_task(Help(self._task_id))
        return Task.Result(args)
