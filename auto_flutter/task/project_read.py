from json import load as json_load

from ..model.project import Project
from ..model.task import Task


class ProjectRead(Task):
    identity = Task.Identity(
        "-project-read", "Reading project file", [], lambda: ProjectRead(False)
    )

    identity_skip = Task.Identity(
        "-project-read-skip", "Reading project file", [], lambda: ProjectRead(True)
    )

    def __init__(self, warn_if_fail: bool) -> None:
        super().__init__()
        self.warn_if_fail: bool = warn_if_fail

    def execute(self, args: Task.Args) -> Task.Result:
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

        return Task.Result(args)

    def __return_error(self, args: Task.Args, error: BaseException) -> Task.Result:
        return Task.Result(args, error, success=self.warn_if_fail)
