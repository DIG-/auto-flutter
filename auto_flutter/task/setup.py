from copy import error
from pathlib import Path, PurePath
from typing import Optional, List
from ..core.arguments import Args, Option
from ..core.os import OS
from ..core.task import Task, TaskIdentity, TaskResult
from ..model.config import Config
from ..model.task_id import TaskId
from ..core.process.process import Process


class SetupCheck(Task):
    def __init__(
        self,
        flutter: bool = False,
        firebase: bool = False,
        skip_on_failure: bool = False,
    ) -> None:
        super().__init__()
        if not flutter and not firebase:
            raise AttributeError("Require check flutter or firebase")
        self._flutter = flutter
        self._firebase = firebase
        self._skip = skip_on_failure

    def describe(self, args: Task.Args) -> str:
        if self._flutter:
            return "Checking fluter"
        elif self._firebase:
            return "Checking firebase"
        return "Unknown checking"

    def execute(self, args: Task.Args) -> Task.Result:
        if self._flutter:
            return self.__test_flutter(args)
        elif self._firebase:
            return self.__test_firebase(args)
        return Task.Result(
            args,
            error=NotImplementedError("Setup check only accept flutter or firebase"),
        )

    def __test_flutter(self, args: Task.Args) -> Task.Result:
        process = Process.create(Config.instance().flutter, ["--version"])
        output = process.try_run()
        if isinstance(output, BaseException):
            return Task.Result(args, error=output, success=self._skip)
        if output == False:
            return Task.Result(
                args,
                error=RuntimeError(
                    "Flutter command return with code #" + str(process.exit_code)
                ),
                success=self._skip,
            )
        return Task.Result(args)

    def __test_firebase(self, args: Task.Args) -> Task.Result:
        env = {"FIREPIT_VERSION": "1"} if Config.instance().firebase_standalone else {}
        process = Process.create(
            Config.instance().firebase, ["--version"], environment=env
        )
        output = process.try_run()
        if isinstance(output, BaseException):
            return Task.Result(args, error=output, success=self._skip)
        if output == False:
            return Task.Result(
                args,
                error=RuntimeError(
                    "Firebase-cli command return with code #" + str(process.exit_code)
                ),
                success=self._skip,
            )
        return Task.Result(args)


class SetupEdit(Task):
    identity = TaskIdentity(
        "-setup-edit",
        "",
        [
            Option(
                None,
                "flutter",
                "Flutter command, can be absolute path if it is not in PATH",
                True,
            ),
            Option(
                None,
                "firebase-cli",
                "Firebase cli command, can be absolute path if it is not in PATH",
                True,
            ),
            Option(
                None,
                "firebase-standalone",
                "When firebase cli is standalone version",
            ),
            Option(
                None,
                "no-firebase-standalone",
                "When firebase cli is not standalone version",
            ),
            Option(
                None,
                "show",
                "Show current config",
            ),
            Option(
                None,
                "check",
                "Check current config",
            ),
        ],
        lambda: SetupEdit(),
    )

    def execute(self, args: Args) -> TaskResult:
        if "show" in args or "check" in args:
            return TaskResult(args)  # Nothing to edit in show mode

        from ..core.task_manager import TaskManager

        if "flutter" in args:
            flutter = args["flutter"].value
            if flutter is None or len(flutter) == 0:
                return TaskResult(
                    args, ValueError("Require valid path for flutter"), False
                )
            path = PurePath(flutter)
            if path.is_absolute():
                if not Path(path).exists():
                    return TaskResult(
                        args,
                        FileNotFoundError(
                            'Can not find flutter in "{}"'.format(flutter)
                        ),
                        False,
                    )
                Config.instance().flutter = OS.machine_to_posix_path(path)
                TaskManager.instance().add(
                    SetupCheck(flutter=True, skip_on_failure=True)
                )

        if "firebase-cli" in args:
            firebase = args["firebase-cli"].value
            if firebase is None or len(firebase) == 0:
                return TaskResult(
                    args, ValueError("Require valid path for firebase-cli"), False
                )
            path = PurePath(firebase)
            if path.is_absolute():
                if not Path(path).exists():
                    return TaskResult(
                        args,
                        FileNotFoundError(
                            'Can not find firebase-cli in "{}"'.format(firebase)
                        ),
                        False,
                    )
                Config.instance().firebase = OS.machine_to_posix_path(path)
                TaskManager.instance().add(
                    SetupCheck(firebase=True, skip_on_failure=True)
                )

        if "firebase-standalone" in args:
            Config.instance().firebase_standalone = True
        elif "no-firebase-standalone" in args:
            Config.instance().firebase_standalone = False

        return TaskResult(args)


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
            from ..core.task_manager import TaskManager

            TaskManager.instance().add(SetupCheck(flutter=True, skip_on_failure=True))
            TaskManager.instance().add(SetupCheck(firebase=True, skip_on_failure=True))
            return Task.Result(args)

        try:
            Config.instance().save()
        except BaseException as error:
            return TaskResult(args, error, success=False)
        return TaskResult(args)
