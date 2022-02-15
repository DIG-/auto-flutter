from typing import List

from ...core.config import Config
from ...model.argument import Args
from ...model.task import *
from ..firebase import FirebaseCheck
from ..flutter import FlutterCheck
from ..options import ParseOptions
from .edit import SetupEdit


class Setup(Task):
    identity: TaskIdentity = TaskIdentity(
        "setup",
        "Edit global config",
        [],
        lambda: Setup(),
    )

    def require(self) -> List[TaskId]:
        return [ParseOptions.identity.id, SetupEdit.identity.id]

    def describe(self, args: Args) -> str:
        if args.contains(SetupEdit.option_show):
            return "Showing current config"
        elif args.contains(SetupEdit.option_check):
            return "Checking current config"
        return "Saving config to file"

    def execute(self, args: Args) -> TaskResult:
        if args.contains(SetupEdit.option_show):
            return TaskResult(args, message=str(Config))

        elif args.contains(SetupEdit.option_check):
            from ...core.task.manager import TaskManager

            manager = TaskManager
            manager.add(FirebaseCheck(skip_on_failure=True))
            manager.add(FlutterCheck(skip_on_failure=True))
            return TaskResult(args)

        try:
            Config.save()
        except BaseException as error:
            return TaskResult(args, error, success=False)
        return TaskResult(args)
