from json import dumps as json_dumps
from pathlib import Path, PurePath
from pprint import pprint
from typing import Optional, Type, List
from ..core.arguments import Args, Option
from ..core.os import OS
from ..core.task import Task, TaskIdentity
from ..model.config import Config
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

    def execute(self, args: Args) -> Optional[Args]:
        if "show" in args:
            return args  # Nothing to edit in show mode

        if "flutter" in args:
            flutter = args["flutter"].value
            if flutter is None or len(flutter) == 0:
                log.error("Require a valid path")
                return None
            path = PurePath(flutter)
            if path.is_absolute():
                if not Path(path).exists():
                    log.error('Can not find flutter in "{}"' % flutter)
                    return None
                Config.instance().flutter = OS.machine_to_posix_path(path)

        if "firebase-cli" in args:
            firebase = args["firebase-cli"].value
            if firebase is None or len(firebase) == 0:
                log.error("Require a valid path")
                return None
            path = PurePath(firebase)
            if path.is_absolute():
                if not Path(path).exists():
                    log.error('Can not find firebase-cli in "{}"' % firebase)
                    return None
                Config.instance().firebase = OS.machine_to_posix_path(path)

        if "firebase-standalone" in args:
            Config.instance().firebase_standalone = True
        elif "no-firebase-standalone" in args:
            Config.instance().firebase_standalone = False

        return args


class Setup(Task):
    identity: TaskIdentity = TaskIdentity(
        "setup",
        "Edit global config",
        [],
        lambda: Setup(),
    )

    def require(self) -> List[Task]:
        return [SetupEdit()]

    def describe(self, args: Args) -> str:
        if "show" in args:
            return "Showing current config"
        return "Saving config to file"

    def execute(self, args: Args) -> Optional[Args]:
        if "show" in args:
            pprint(Config.instance())
            return args

        try:
            Config.instance().save()
        except:
            log.error("Failed to save config")
            return None
        return args
