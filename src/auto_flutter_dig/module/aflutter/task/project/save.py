from json import dump as json_dump

from .....core.json import _JsonEncode
from .....model.project import Project
from .....model.task import *
from ...identity import AflutterTaskIdentity


class ProjectSave(Task):
    identity = AflutterTaskIdentity("-project-save", "Saving project file", [], lambda: ProjectSave())

    def execute(self, args: Args) -> TaskResult:
        project = Project.current
        if project is None:
            raise ValueError("There is no project to save")
        try:
            file = open("aflutter.json", "wt")
        except BaseException as error:
            return TaskResult(args, error=error)

        try:
            json = _JsonEncode.clear_nones(project.to_json())
        except BaseException as error:
            raise RuntimeError("Failed to serialize project", error)

        json_dump(json, file, indent=2)
        file.close()
        return TaskResult(args)
