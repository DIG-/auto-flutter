from .....core.config import Config
from .....core.os.executable_resolver import ExecutableResolver
from .....core.os.path_converter import PathConverter
from .....core.string import SB
from .....model.argument.option import LongPositionalOption
from .....model.task import *
from .....module.aflutter.task.setup.save import AflutterSetupSaveTask
from ...identity import FlutterTaskIdentity
from ...model._const import FLUTTER_CONFIG_KEY_PATH
from .check import FlutterSetupCheckTask


class FlutterSetupTask(Task):
    __opt_executable = LongPositionalOption("command", 0, "Set flutter command, will be absolute if not in PATH")
    identity = FlutterTaskIdentity(
        "flutter",
        "Configure flutter environment",
        [__opt_executable],
        lambda: FlutterSetupTask(),
    )

    def execute(self, args: Args) -> TaskResult:
        had_change = False
        if args.contains(self.__opt_executable):
            flutter_cmd = args.get(self.__opt_executable)
            if flutter_cmd is None or len(flutter_cmd) <= 0:
                return TaskResult(args, E(ValueError("Invalid flutter command")).error)
            flutter_path = PathConverter.from_path(flutter_cmd).to_posix()
            flutter_exec = ExecutableResolver.resolve_executable(flutter_path)
            if flutter_exec is None:
                error = E(FileNotFoundError('Can not find flutter command as "{}"'.format(flutter_cmd))).error
                message = (
                    SB().append("Resolved as: ", SB.Color.YELLOW).append(str(flutter_path), SB.Color.YELLOW, True).str()
                )
                return TaskResult(
                    args,
                    error=error,
                    message=message,
                    success=False,
                )
            Config.put_path(FLUTTER_CONFIG_KEY_PATH, flutter_exec)
            had_change = True

        if not had_change:
            return TaskResult(args, Warning("Nothing was changed"), success=True)

        self._append_task([AflutterSetupSaveTask.identity, FlutterSetupCheckTask.identity])
        return TaskResult(args)
