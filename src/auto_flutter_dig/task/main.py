import sys

from ..core.config import Config
from ..core.string import SB
from ..model.error import E, SilentWarning, TaskNotFound
from ..model.task import *
from ..task.help import Help
from ..task.identity import AflutterTaskIdentity
from ..task.options import ParseOptions
from ..task.project import ProjectRead


class ReadConfigTask(Task):
    identity = AflutterTaskIdentity(
        "-read-aflutter-config", "", [], lambda: ReadConfigTask()
    )

    def describe(self, args: Args) -> str:
        return "Reading config"

    def execute(self, args: Args) -> TaskResult:
        loaded = False
        base_error = Warning("Failed to read config. Using default values.")
        try:
            loaded = Config.load()
        except BaseException as error:
            base_error = E(base_error).caused_by(error)
        if loaded:
            return TaskResult(args)
        return TaskResult(
            args,
            error=base_error,
            message=SB()
            .append("Use task ", end="")
            .append("setup", SB.Color.CYAN, True)
            .append(" to configure your environment")
            .str(),
            success=True,
        )


class MainTask(Task):
    def __init__(self, first_load: bool = True) -> None:
        super().__init__()
        self.__first_load = first_load

    def describe(self, args: Args) -> str:
        return "Resolve task"

    def execute(self, args: Args) -> TaskResult:
        if len(sys.argv) <= 1:
            self._append_task(
                Help.Stub(
                    message=SB()
                    .append("Auto-Flutter requires at least one task", SB.Color.RED)
                    .str()
                )
            )
            return TaskResult(args, SilentWarning(), success=True)
        task_id = sys.argv[1].lower()
        if task_id.startswith("-"):
            if task_id in ("-h", "--help"):
                self._append_task(Help.Stub())
                return TaskResult(args)
            else:
                self._append_task(Help.Stub(task_id))
                return TaskResult(args, SilentWarning(), success=True)

        try:
            self._append_task_id(task_id)
        except TaskNotFound as error:
            if self.__first_load:
                self._append_task(MainTask(False))
                self._append_task(ProjectRead.identity_skip)
            else:
                self._append_task(Help.Stub(task_id))
            return TaskResult(args, E(SilentWarning()).caused_by(error), success=True)
        except BaseException as error:
            return TaskResult(
                args,
                E(LookupError("Failed to append task {}".format(task_id))).caused_by(
                    error
                ),
            )

        self._append_task(ParseOptions())

        return TaskResult(args)

    pass
