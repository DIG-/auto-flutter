from pathlib import Path, PurePath
from typing import Final

from ...core.os import OS
from ...model.config import Config
from ...model.task import Task
from ..firebase.check import FirebaseCheck
from .check_flutter import SetupCheckFlutter


class SetupEdit(Task):
    option_flutter: Final = Task.Option(
        None,
        "flutter",
        "Flutter command, can be absolute path if it is not in PATH",
        True,
    )
    option_firebase: Final = Task.Option(
        None,
        "firebase-cli",
        "Firebase cli command, can be absolute path if it is not in PATH",
        True,
    )
    option_firebase_standalone: Final = Task.Option(
        None,
        "firebase-standalone",
        "When firebase cli is standalone version",
    )
    option_firebase_non_standalone: Final = Task.Option(
        None,
        "no-firebase-standalone",
        "When firebase cli is not standalone version",
    )
    option_show: Final = Task.Option(None, "show", "Show current config")
    option_check: Final = Task.Option(None, "check", "Check current config")

    identity = Task.Identity(
        "-setup-edit",
        "",
        [
            option_flutter,
            option_firebase,
            option_firebase_standalone,
            option_firebase_non_standalone,
            option_show,
            option_check,
        ],
        lambda: SetupEdit(),
    )

    def execute(self, args: Task.Args) -> Task.Result:
        if args.contains(self.option_show) or args.contains(self.option_check):
            return Task.Result(args)  # Nothing to edit in show mode

        from ...core.task.manager import TaskManager

        manager: Final = TaskManager.instance()

        if args.contains(self.option_flutter):
            flutter: Final = args.get_value(self.option_flutter)
            if flutter is None or len(flutter) == 0:
                return Task.Result(
                    args, ValueError("Require valid path for flutter"), False
                )
            path = PurePath(flutter)
            if path.is_absolute():
                if not Path(path).exists():
                    return Task.Result(
                        args,
                        FileNotFoundError(
                            'Can not find flutter in "{}"'.format(flutter)
                        ),
                        False,
                    )
                Config.instance().flutter = OS.machine_to_posix_path(path)
                manager.add(SetupCheckFlutter(skip_on_failure=True))

        if args.contains(self.option_firebase):
            firebase: Final = args.get_value(self.option_firebase)
            if firebase is None or len(firebase) == 0:
                return Task.Result(
                    args, ValueError("Require valid path for firebase-cli"), False
                )
            path = PurePath(firebase)
            if path.is_absolute():
                if not Path(path).exists():
                    return Task.Result(
                        args,
                        FileNotFoundError(
                            'Can not find firebase-cli in "{}"'.format(firebase)
                        ),
                        False,
                    )
                Config.instance().firebase = OS.machine_to_posix_path(path)
                manager.add(FirebaseCheck(skip_on_failure=True))

        if args.contains(self.option_firebase_standalone):
            Config.instance().firebase_standalone = True
        elif args.contains(self.option_firebase_non_standalone):
            Config.instance().firebase_standalone = False

        return Task.Result(args)
