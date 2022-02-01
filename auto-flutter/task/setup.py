from math import fabs
from pathlib import Path, PurePath
from pprint import pprint
from typing import Optional, List
from ..core.arguments import Args, Option
from ..core.os import OS
from ..core.task import Task, TaskIdentity, TaskResult
from ..model.config import Config
from ..model.task_id import TaskId
from ..core.logger import log


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
        ],
        lambda: SetupEdit(),
    )

    def execute(self, args: Args) -> TaskResult:
        if "show" in args:
            return TaskResult(args)  # Nothing to edit in show mode

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
        return "Saving config to file"

    def execute(self, args: Args) -> TaskResult:
        if "show" in args:
            pprint(Config.instance())
            return TaskResult(args)

        try:
            Config.instance().save()
        except BaseException as error:
            return TaskResult(args, error, False)
        return TaskResult(args)
