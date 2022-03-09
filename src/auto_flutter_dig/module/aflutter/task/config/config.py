from .....model.task import *
from .....model.task.group import TaskGroup
from .....task.base.subtask_parent_task import BaseSubtaskParentTask
from ...identity import AflutterTaskIdentity
from .flavor import AflutterFlavorConfigTask
from .platform import AflutterPlatformConfigTask
from .refresh import AflutterConfigRefreshTask

__all__ = ["AflutterConfigIdentity"]


class _AflutterConfigIdentity(AflutterTaskIdentity, TaskGroup):
    def __init__(self) -> None:
        AflutterTaskIdentity.__init__(
            self,
            "config",
            "Configure project",
            [],
            lambda: BaseSubtaskParentTask(self, self),
        )
        TaskGroup.__init__(
            self,
            [
                AflutterConfigRefreshTask.identity,
                AflutterPlatformConfigTask.identity,
                AflutterFlavorConfigTask.identity,
            ],
        )


AflutterConfigIdentity = _AflutterConfigIdentity()
