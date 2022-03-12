from typing import Callable

from .......core.utils import _Dict
from .......model.task import *
from .......model.task.init.project_identity import InitProjectTaskIdentity
from .......model.task.group import TaskGroup
from .....identity import AflutterTaskIdentity
from ..find.flavor.flavor import ProjectInitFindFlavorTask
from .android import ProjectInitConfigAndroidTask
from .ios import ProjectInitConfigIosTask
from .web import ProjectInitConfigWebTask


class ProjectInitConfigIdentity(AflutterTaskIdentity, InitProjectTaskIdentity, TaskGroup):
    def __init__(self, creator: Callable[[], Task]) -> None:
        InitProjectTaskIdentity.__init__(self, "", "", "", [], creator)
        AflutterTaskIdentity.__init__(self, "-project-init-config", "", [], creator)
        TaskGroup.__init__(
            self,
            [
                ProjectInitConfigAndroidTask.identity,
                ProjectInitConfigIosTask.identity,
                ProjectInitConfigWebTask.identity,
            ],
        )

    @property
    def require_before(self) -> List[TaskIdentity]:
        return [ProjectInitFindFlavorTask.identity]


class ProjectInitConfigTask(Task):
    identity: ProjectInitConfigIdentity = ProjectInitConfigIdentity(
        lambda: ProjectInitConfigTask(ProjectInitConfigTask.identity)
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
