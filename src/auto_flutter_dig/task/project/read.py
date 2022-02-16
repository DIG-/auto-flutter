from json import load as json_load

from ...core.string import SB
from ...model.project import Project
from ...model.task import *
from .inport import ProjectTaskImport


class ProjectRead(Task):
    identity = TaskIdentity(
        "-project-read", "Reading project file", [], lambda: ProjectRead(False)
    )

    identity_skip = TaskIdentity(
        "-project-read-skip", "Reading project file", [], lambda: ProjectRead(True)
    )

    _warn_if_fail: bool

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
            return self.__return_error(args, error)

        if file is None:
            return self.__return_error(
                args, FileNotFoundError("Can not open project file for read")
            )

        try:
            json = json_load(file)
        except BaseException as error:
            return self.__return_error(args, error)

        try:
            Project.current = Project.from_json(json)
        except BaseException as error:
            return self.__return_error(args, error)

        if not Project.current.tasks is None:
            self._append_task(ProjectTaskImport())

        return TaskResult(args)

    def __return_error(self, args: Args, error: BaseException) -> TaskResult:
        return TaskResult(args, error, success=self._warn_if_fail)
