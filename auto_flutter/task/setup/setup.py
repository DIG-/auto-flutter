from typing import List

from ...model.argument import Args
from ...model.config import Config
from ...model.task import Task, TaskId, TaskIdentity, TaskResult
from .check import SetupCheck
from .edit import SetupEdit


class Setup(Task):
    identity: TaskIdentity = TaskIdentity(
        "setup",
        "Edit global config",
        [],
        lambda: Setup(),
    )

    def require(self) -> List[TaskId]:
        return [SetupEdit.identity.id]

    def describe(self, args: Args) -> str:
        if "show" in args:
            return "Showing current config"
        elif "check" in args:
            return "Checking current config"
        return "Saving config to file"

    def execute(self, args: Args) -> TaskResult:
        if "show" in args:
            return TaskResult(args, message=str(Config.instance()))
        elif "check" in args:
            from ...core.task.manager import TaskManager

            TaskManager.instance().add(SetupCheck(flutter=True, skip_on_failure=True))
            TaskManager.instance().add(SetupCheck(firebase=True, skip_on_failure=True))
            return Task.Result(args)

        try:
            Config.instance().save()
        except BaseException as error:
            return TaskResult(args, error, success=False)
        return TaskResult(args)
