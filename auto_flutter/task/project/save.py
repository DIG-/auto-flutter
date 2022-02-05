from json import dump as json_dump

from ...model.project import Project
from ...model.task import Task


class ProjectSave(Task):
    identity = Task.Identity(
        "-project-save", "Saving project", [], lambda: ProjectSave()
    )

    def execute(self, args: Task.Args) -> Task.Result:
        project = Project.current
        if project is None:
            raise ValueError("There is no project to save")
        try:
            file = open("aflutter.json", "wt")
        except BaseException as error:
            return Task.Result(args, error=error)

        try:
            json = project.to_json()
        except BaseException as error:
            raise RuntimeError("Failed to serialize project", error)

        json_dump(json, file)
        return Task.Result(args)
