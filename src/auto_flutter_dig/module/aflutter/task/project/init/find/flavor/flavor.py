from typing import Callable

from ........core.utils import _Dict
from ........model.task import *
from ........model.task.init.project_identity import InitProjectTaskIdentity
from ........model.task.group import TaskGroup
from ......identity import AflutterTaskIdentity
from ..platform import ProjectInitFindPlatformTask
from .android_gradle import ProjectInitFindFlavorAndroidGradleTask
from .intellij import ProjectInitFindFlavorIntellijTask
from .ios import ProjectInitFindFlavorIosTask
from .web import ProjectInitFindFlavorWebTask


class ProjectInitFindFlavorIdentity(AflutterTaskIdentity, InitProjectTaskIdentity, TaskGroup):
    def __init__(self, creator: Callable[[], Task]) -> None:
        InitProjectTaskIdentity.__init__(self, "", "", "", [], creator)
        AflutterTaskIdentity.__init__(self, "-project-init-find-flavor", "", [], creator)
        TaskGroup.__init__(
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

    def __init__(self, subtask: TaskGroup) -> None:
        super().__init__()
        self._subtask = subtask

    def describe(self, args: Args) -> str:
        return ""

    def execute(self, args: Args) -> TaskResult:
        tasks = _Dict.flatten(self._subtask.subtasks)
        tasks.reverse()
        self._append_task(tasks)
        return TaskResult(args)
