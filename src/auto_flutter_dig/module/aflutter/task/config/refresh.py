from .....model.task import *
from .base import BaseConfigTask
from .project import ProjectConfigTaskIdentity


class AflutterConfigRefreshTask(BaseConfigTask):
    identity = ProjectConfigTaskIdentity(
        "refresh",
        "Update aflutter.json with aflutter style. Usefully after manually editing aflutter.json",
        [],
        lambda: AflutterConfigRefreshTask(),
    )

    def describe(self, args: Args) -> str:
        return "Refresh project file"

    def execute(self, args: Args) -> TaskResult:
        self._add_save_project()
        return TaskResult(args)
