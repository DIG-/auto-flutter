from typing import Final, List

from ...model.argument import Args
from ...model.config import Config
from ...model.task import Task
from ..firebase import FirebaseCheck
from ..flutter import FlutterCheck
from .edit import SetupEdit


class Setup(Task):
    identity: Task.Identity = Task.Identity(
        "setup",
        "Edit global config",
        [],
        lambda: Setup(),
    )

    def require(self) -> List[Task.ID]:
        return [SetupEdit.identity.id]

    def describe(self, args: Args) -> str:
        if args.contains(SetupEdit.option_show):
            return "Showing current config"
        elif args.contains(SetupEdit.option_check):
            return "Checking current config"
        return "Saving config to file"

    def execute(self, args: Args) -> Task.Result:
        if args.contains(SetupEdit.option_show):
            return Task.Result(args, message=str(Config.instance()))

        elif args.contains(SetupEdit.option_check):
            from ...core.task.manager import TaskManager

            manager: Final = TaskManager.instance()
            manager.add(FirebaseCheck(skip_on_failure=True))
            manager.add(FlutterCheck(skip_on_failure=True))
            return Task.Result(args)

        try:
            Config.instance().save()
        except BaseException as error:
            return Task.Result(args, error, success=False)
        return Task.Result(args)
