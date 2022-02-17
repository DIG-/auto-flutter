from typing import Optional

from ...core.config import Config
from ...core.os import ExecutableResolver, PathConverter
from ...core.string import SB
from ...model.task import *
from ..firebase import FirebaseCheck
from ..flutter import FlutterCheck


class SetupEdit(Task):
    option_flutter = Option(
        None,
        "flutter",
        "Flutter command, can be absolute path if it is not in PATH",
        True,
    )
    option_firebase = Option(
        None,
        "firebase-cli",
        "Firebase cli command, can be absolute path if it is not in PATH",
        True,
    )
    option_firebase_standalone = Option(
        None,
        "firebase-standalone",
        "When firebase cli is standalone version",
    )
    option_firebase_non_standalone = Option(
        None,
        "no-firebase-standalone",
        "When firebase cli is not standalone version",
    )
    option_show = Option(None, "show", "Show current config")
    option_check = Option(None, "check", "Check current config")

    identity = TaskIdentity(
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

    def describe(self, args: Args) -> str:
        if args.contains(self.option_show) or args.contains(self.option_check):
            return ""
        return "Editing config"

    def execute(self, args: Args) -> TaskResult:
        if args.contains(self.option_show) or args.contains(self.option_check):
            return TaskResult(args)  # Nothing to edit in show mode

        error: BaseException
        message: Optional[str] = None

        if args.contains(self.option_flutter):
            flutter = args.get_value(self.option_flutter)
            if flutter is None or len(flutter) == 0:
                return TaskResult(
                    args, ValueError("Require valid path for flutter"), success=False
                )
            flutter_path = PathConverter.from_path(flutter).to_posix()
            flutter_exec = ExecutableResolver.resolve_executable(flutter_path)
            if flutter_exec is None:
                error = FileNotFoundError(
                    'Can not find flutter executable in "{}"'.format(flutter)
                )
                message = (
                    SB()
                    .append("Resolved as: ", SB.Color.YELLOW)
                    .append(str(flutter_path), SB.Color.YELLOW, True)
                    .str()
                )
                return TaskResult(
                    args,
                    error=error,
                    message=message,
                    success=False,
                )
            Config.put_path("flutter", flutter_exec)
            self._append_task(FlutterCheck(skip_on_failure=True))

        if args.contains(self.option_firebase):
            firebase = args.get_value(self.option_firebase)
            if firebase is None or len(firebase) == 0:
                return TaskResult(
                    args,
                    ValueError("Require valid path for firebase-cli"),
                    success=False,
                )
            firebase_path = PathConverter.from_path(firebase).to_posix()
            firebase_exec = ExecutableResolver.resolve_executable(firebase_path)
            if firebase_exec is None:
                error = FileNotFoundError(
                    'Can not find firebase-cli in "{}"'.format(firebase)
                )
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
            Config.put_path("firebase", firebase_exec)
            self._append_task(FirebaseCheck(skip_on_failure=True))

        if args.contains(self.option_firebase_standalone):
            Config.put_bool("firebase-standalone", True)
        elif args.contains(self.option_firebase_non_standalone):
            Config.put_bool("firebase-standalone", False)

        return TaskResult(args)
