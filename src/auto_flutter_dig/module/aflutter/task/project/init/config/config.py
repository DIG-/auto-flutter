from typing import Callable

from .......model.task import *
from .......model.task.init.project_identity import InitProjectTaskIdentity
from .......model.task.subtask import Subtask
from .....identity import AflutterTaskIdentity
from ..find.flavor.flavor import ProjectInitFindFlavorTask


class ProjectInitConfigIdentity(AflutterTaskIdentity, InitProjectTaskIdentity, Subtask):
    def __init__(self, creator: Callable[[], Task]) -> None:
        InitProjectTaskIdentity.__init__(self, "", "", "", [], creator)
        AflutterTaskIdentity.__init__(self, "-project-init-config", "", [], creator)
        Subtask.__init__(
            self,
            [],
        )

    @property
    def require_before(self) -> List[TaskIdentity]:
        return [ProjectInitFindFlavorTask.identity]


class ProjectInitConfigTask(Task):
    identity: ProjectInitConfigIdentity = ProjectInitConfigIdentity(
        lambda: ProjectInitConfigTask(ProjectInitConfigTask.identity)
    )

    def __init__(self, subtask: Subtask) -> None:
        super().__init__()
        self._subtask = subtask

    def describe(self, args: Args) -> str:
        return ""

    def execute(self, args: Args) -> TaskResult:
        self._append_task(map(lambda x: x[1], self._subtask.subtasks.items()))
        return TaskResult(args)
