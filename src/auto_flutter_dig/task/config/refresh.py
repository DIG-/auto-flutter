from typing import List

from ...model.task import *
from ...task.identity import AflutterTaskIdentity
from ..project import ProjectRead, ProjectSave


class ConfigRefresh(Task):
    identity = AflutterTaskIdentity(
        "refresh",
        "Update aflutter.json with aflutter style. Usefully after manually editing aflutter.json",
        [],
        lambda: ConfigRefresh(),
    )

    def describe(self, args: Args) -> str:
        return ""

    def require(self) -> List[TaskId]:
        return [ProjectRead.identity.id, ProjectSave.identity.id]

    def execute(self, args: Args) -> TaskResult:
        return TaskResult(args)
