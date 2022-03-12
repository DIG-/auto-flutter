from json import load as json_load

from .....model.error import E, SilentWarning
from .....model.project import Project
from .....model.task import *
from ...identity import AflutterTaskIdentity
from .inport import ProjectTaskImport


class ProjectRead(Task):
    identity = AflutterTaskIdentity("-project-read", "Reading project file", [], lambda: ProjectRead(False))

    identity_skip = AflutterTaskIdentity("-project-read-skip", "Reading project file", [], lambda: ProjectRead(True))

    def __init__(self, warn_if_fail: bool) -> None:
        super().__init__()
        self._warn_if_fail = warn_if_fail

    def describe(self, args: Args) -> str:
        if not Project.current is None:
            return ""
        return super().describe(args)

    def execute(self, args: Args) -> TaskResult:
        if not Project.current is None:
            return TaskResult(args)
        try:
            file = open("aflutter.json", "r")
        except BaseException as error:
            if self._warn_if_fail:
                return self.__return_error(
                    args,
                    E(SilentWarning('Failed to open file "aflutter.json"')).caused_by(error),
                )
            return self.__return_error(
                args,
                E(FileNotFoundError('Failed to open file "aflutter.json"')).caused_by(error),
            )

        if file is None:
            return self.__return_error(args, E(FileNotFoundError("Can not open project file for read")).error)

        try:
            json = json_load(file)
        except BaseException as error:
            return self.__return_error(
                args,
                E(RuntimeError('Failed to read file "afutter.json"')).caused_by(error),
            )

        try:
            Project.current = Project.from_json(json)
        except BaseException as error:
            return self.__return_error(
                args,
                E(ValueError('Failed to parse project from "aflutter.json"')).caused_by(error),
            )

        if not Project.current.tasks is None:
            self._append_task(ProjectTaskImport())

        return TaskResult(args)

    def __return_error(self, args: Args, error: BaseException) -> TaskResult:
        return TaskResult(args, error, success=self._warn_if_fail)
