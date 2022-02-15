from enum import Enum, auto
from os import X_OK as os_X_OK
from os import access as os_access
from os import environ as os_environ
from pathlib import Path
from typing import List, Optional, Tuple

from ...core.config import Config
from ...core.os import OS
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
            found = SetupEdit.__parse_path(flutter)
            if found[0] in (
                SetupEdit.__PathResult.NOT_FOUND,
                SetupEdit.__PathResult.NOT_EXECUTABLE,
            ):
                error = FileNotFoundError(
                    'Can not find flutter in "{}"'.format(flutter)
                )
                if found[0] == SetupEdit.__PathResult.NOT_EXECUTABLE:
                    error = FileNotFoundError('Not executable in "{}"'.format(flutter))
                message = None
                if not found[1] is None:
                    message = (
                        SB()
                        .append("Resolved as: ", SB.Color.YELLOW)
                        .append(str(found[1]), SB.Color.YELLOW, True)
                        .str()
                    )
                return TaskResult(
                    args,
                    error=error,
                    message=message,
                    success=False,
                )
            if found[1] is None:
                return TaskResult(
                    args, RuntimeError("Path was expected, but nothing appears")
                )
            Config.put_path("flutter", OS.machine_to_posix_path(found[1]))
            self._append_task(FlutterCheck(skip_on_failure=True))

        if args.contains(self.option_firebase):
            firebase = args.get_value(self.option_firebase)
            if firebase is None or len(firebase) == 0:
                return TaskResult(
                    args,
                    ValueError("Require valid path for firebase-cli"),
                    success=False,
                )
            found = SetupEdit.__parse_path(firebase)
            if found[0] in (
                SetupEdit.__PathResult.NOT_FOUND,
                SetupEdit.__PathResult.NOT_EXECUTABLE,
            ):
                error = FileNotFoundError(
                    'Can not find firebase-cli in "{}"'.format(firebase)
                )
                if found[0] == SetupEdit.__PathResult.NOT_EXECUTABLE:
                    error = FileNotFoundError('Not executable in "{}"'.format(firebase))
                message = None
                if not found[1] is None:
                    message = (
                        SB()
                        .append("Resolved as: ", SB.Color.YELLOW)
                        .append(str(found[1]), SB.Color.YELLOW, True)
                        .str()
                    )
                return TaskResult(
                    args,
                    error=error,
                    message=message,
                    success=False,
                )
            if found[1] is None:
                return TaskResult(
                    args, RuntimeError("Path was expected, but nothing appears")
                )
            Config.put_path("firebase", OS.machine_to_posix_path(found[1]))
            self._append_task(FirebaseCheck(skip_on_failure=True))

        if args.contains(self.option_firebase_standalone):
            Config.put_bool("firebase-standalone", True)
        elif args.contains(self.option_firebase_non_standalone):
            Config.put_bool("firebase-standalone", False)

        return TaskResult(args)

    class __PathResult(Enum):
        FOUND = auto()
        NOT_FOUND = auto()
        NOT_EXECUTABLE = auto()

    __FindResult = Tuple[__PathResult, Optional[Path]]

    @staticmethod
    def __parse_path(initial: str) -> __FindResult:
        path: Path = Path(initial)
        if path.is_absolute():
            if not path.exists():
                return (SetupEdit.__PathResult.NOT_FOUND, None)
            return SetupEdit.__check_if_executable(path.resolve())
        if path.parent == Path("."):
            if path.exists():
                # Local file, make absolute
                return SetupEdit.__check_if_executable(path.resolve())
            if not SetupEdit.__check_if_in_sys_path(path):
                return (SetupEdit.__PathResult.NOT_FOUND, None)
            return (SetupEdit.__PathResult.FOUND, path)
        return SetupEdit.__check_if_executable(path.resolve())

    @staticmethod
    def __check_if_executable(path: Path) -> __FindResult:
        if OS.current() == OS.WINDOWS:
            if path.suffix.lower() in (".exe", ".bat", ".cmd"):
                return (SetupEdit.__PathResult.FOUND, path)
            elif len(path.suffix) <= 0:
                npath = path.with_suffix(".exe")
                if npath.exists():
                    return (SetupEdit.__PathResult.FOUND, npath)
                npath = path.with_suffix(".bat")
                if npath.exists():
                    return (SetupEdit.__PathResult.FOUND, npath)
                npath = path.with_suffix(".cmd")
                if npath.exists():
                    return (SetupEdit.__PathResult.FOUND, npath)
            return (SetupEdit.__PathResult.NOT_EXECUTABLE, path)
        ## Not Windows
        if os_access(path, os_X_OK):
            return (SetupEdit.__PathResult.FOUND, path)
        return (SetupEdit.__PathResult.NOT_EXECUTABLE, path)

    @staticmethod
    def __check_if_in_sys_path(path: Path) -> bool:
        for node in SetupEdit.__get_environ_path():
            current: Path = Path(node)
            if not current.exists():
                continue
            current /= path
            if current.exists():
                return True
        return False

    @staticmethod
    def __get_environ_path() -> List[str]:
        path: Optional[str] = None
        if "PATH" in os_environ:
            path = os_environ["PATH"]
        elif "path" in os_environ:
            path = os_environ["path"]
        elif "Path" in os_environ:
            path = os_environ["Path"]
        if path is None:
            return []
        if OS.current() == OS.WINDOWS:
            return path.split(";")
        return path.split(":")
