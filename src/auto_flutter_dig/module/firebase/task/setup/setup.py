from .....core.config import Config
from .....core.os.executable_resolver import ExecutableResolver
from .....core.os.path_converter import PathConverter
from .....core.string import SB
from .....model.argument.option import LongOption, LongPositionalOption
from .....model.task import *
from .....module.aflutter.task.setup.save import AflutterSetupSaveTask
from ...identity import FirebaseTaskIdentity
from ...model._const import FIREBASE_CONFIG_KEY_PATH, FIREBASE_CONFIG_KEY_STANDALONE
from .check import FirebaseCheck


class FirebaseSetupTask(Task):
    __opt_executable = LongPositionalOption("command", 0, "Set firebase command, will be absolute if not in PATH")
    __opt_standalone_on = LongOption("standalone", "Set flag to handle firebase as standalone build")
    __opt_standalone_off = LongOption("no-standalone", "Remove flag of firebase standalone")
    identity = FirebaseTaskIdentity(
        "firebase",
        "Configure firebase environment",
        [__opt_executable, __opt_standalone_on, __opt_standalone_off],
        lambda: FirebaseSetupTask(),
    )

    def execute(self, args: Args) -> TaskResult:
        had_change = False
        if args.contains(self.__opt_executable):
            firebase_cmd = args.get(self.__opt_executable)
            if firebase_cmd is None or len(firebase_cmd) <= 0:
                return TaskResult(args, ValueError("Invalid firebase command"))
            firebase_path = PathConverter.from_path(firebase_cmd).to_posix()
            firebase_exec = ExecutableResolver.resolve_executable(firebase_path)
            if firebase_exec is None:
                error = FileNotFoundError('Can not find firebase command as "{}"'.format(firebase_cmd))
                message = (
                    SB()
                    .append("Resolved as: ", SB.Color.YELLOW)
                    .append(str(firebase_path), SB.Color.YELLOW, True)
                    .str()
                )
                return TaskResult(
                    args,
                    error=error,
                    message=message,
                    success=False,
                )
            Config.put_path(FIREBASE_CONFIG_KEY_PATH, firebase_exec)
            had_change = True

        if args.contains(self.__opt_standalone_on):
            if args.contains(self.__opt_standalone_off):
                self._print(
                    SB()
                    .append(
                        "Can not enable and disable standalone mode simultaneously",
                        SB.Color.YELLOW,
                    )
                    .str()
                )
            Config.put_bool(FIREBASE_CONFIG_KEY_STANDALONE, True)
            had_change = True
        elif args.contains(self.__opt_standalone_off):
            Config.remove(FIREBASE_CONFIG_KEY_STANDALONE)
            had_change = True

        if not had_change:
            return TaskResult(args, Warning("Nothing was changed"), success=True)

        self._append_task([AflutterSetupSaveTask.identity, FirebaseCheck.identity])
        return TaskResult(args)
