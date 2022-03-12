from pprint import pprint
from .....core.config import Config
from .....model.error import E
from .....model.task import *
from .....module.aflutter.identity import AflutterTaskIdentity

__all__ = ["AflutterSetupSaveTask"]


class AflutterSetupSaveTask(Task):
    identity = AflutterTaskIdentity(
        "-aflutter-setup-save",
        "Save current environment config",
        [],
        lambda: AflutterSetupSaveTask(),
    )

    def describe(self, args: Args) -> str:
        return "Saving environment config"

    def execute(self, args: Args) -> TaskResult:
        try:
            Config.save()
        except BaseException as error:
            return TaskResult(
                args,
                error=E(RuntimeError("Failed to save environment config")).caused_by(error),
            )
        return TaskResult(args)
