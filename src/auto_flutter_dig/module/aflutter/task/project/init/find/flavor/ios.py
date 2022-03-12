from ........model.error.silent_warning import SilentWarning
from ........model.platform import Platform
from ........model.project import Project
from ........model.task import *
from .base import BaseProjectInitFindFlavorIdentity, BaseProjectInitFindFlavorTask


class ProjectInitFindFlavorIosTask(BaseProjectInitFindFlavorTask):
    identity = BaseProjectInitFindFlavorIdentity(
        "-project-init-find-flavor-1-ios",
        "",
        [],
        lambda: ProjectInitFindFlavorIosTask(),  # pylint: disable=unnecessary-lambda
    )

    def describe(self, args: Args) -> str:
        return "Detect flavor config via iOS"

    def execute(self, args: Args) -> TaskResult:
        project = Project.current
        if not Platform.IOS in project.platforms:
            self._uptade_description("")
            return TaskResult(args, E(SilentWarning("Project does not support ios platform")).error, success=True)

        return TaskResult(args, E(NotImplementedError("Not implemented yet")).error, success=True)
