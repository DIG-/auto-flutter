from typing import Callable

from ........model.task import *
from ........model.task.init.project_identity import InitProjectTaskIdentity
from ........model.task.subtask import Subtask
from ......identity import AflutterTaskIdentity
from ..platform import ProjectInitFindPlatformTask
from .android_gradle import ProjectInitFindFlavorAndroidGradleTask
from .intellij import ProjectInitFindFlavorIntellijTask
from .ios import ProjectInitFindFlavorIosTask
from .web import ProjectInitFindFlavorWebTask


class ProjectInitFindFlavorIdentity(AflutterTaskIdentity, InitProjectTaskIdentity, Subtask):
    def __init__(self, creator: Callable[[], Task]) -> None:
        InitProjectTaskIdentity.__init__(self, "", "", "", [], creator)
        AflutterTaskIdentity.__init__(self, "-project-init-find-flavor", "", [], creator)
        Subtask.__init__(
            self,
            [
                ProjectInitFindFlavorIntellijTask.identity,
                ProjectInitFindFlavorAndroidGradleTask.identity,
                ProjectInitFindFlavorIosTask.identity,
                ProjectInitFindFlavorWebTask.identity,
            ],
        )

    @property
    def require_before(self) -> List[TaskIdentity]:
        return [ProjectInitFindPlatformTask.identity]


class ProjectInitFindFlavorTask(Task):
    identity: ProjectInitFindFlavorIdentity = ProjectInitFindFlavorIdentity(
        lambda: ProjectInitFindFlavorTask(ProjectInitFindFlavorTask.identity)
    )

    def __init__(self, subtask: Subtask) -> None:
        super().__init__()
        self._subtask = subtask

    def describe(self, args: Args) -> str:
        return ""

    def execute(self, args: Args) -> TaskResult:
        self._append_task(map(lambda x: x[1], self._subtask.subtasks.items()))
        return TaskResult(args)
