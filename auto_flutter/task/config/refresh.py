from typing import List

from ...model.task import Task
from ..project import ProjectRead, ProjectSave


class ConfigRefresh(Task):
    identity = Task.Identity(
        "refresh",
        "Update aflutter.json with aflutter style. Usefully after manually editing aflutter.json",
        [],
        lambda: ConfigRefresh(),
    )

    def describe(self, args: Task.Args) -> str:
        return ""

    def require(self) -> List[Task.ID]:
        return [ProjectRead.identity.id, ProjectSave.identity.id]

    def execute(self, args: Task.Args) -> Task.Result:
        return Task.Result(args)
