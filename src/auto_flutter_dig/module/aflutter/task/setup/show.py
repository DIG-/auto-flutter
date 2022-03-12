from .....core.config import Config
from .....model.task import *
from .....module.aflutter.identity import AflutterTaskIdentity


class AflutterSetupShow(Task):
    identity = AflutterTaskIdentity("show", "Show current environment config", [], lambda: AflutterSetupShow())

    def execute(self, args: Args) -> TaskResult:
        return TaskResult(args, message=str(Config), success=True)
