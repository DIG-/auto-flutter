from .....model.task import *
from .....model.task.subtask import Subtask
from .....task.base.subtask_parent_task import BaseSubtaskParentTask
from ...identity import AflutterTaskIdentity
from .flavor import AflutterFlavorConfigTask
from .platform import AflutterPlatformConfigTask
from .refresh import AflutterConfigRefreshTask

__all__ = ["AflutterConfigIdentity"]


class _AflutterConfigIdentity(AflutterTaskIdentity, Subtask):
    def __init__(self) -> None:
        AflutterTaskIdentity.__init__(
            self,
            "config",
            "Configure project",
            [],
            lambda: BaseSubtaskParentTask(self, self),
        )
        Subtask.__init__(
            self,
            [
                AflutterConfigRefreshTask.identity,
                AflutterPlatformConfigTask.identity,
                AflutterFlavorConfigTask.identity,
            ],
        )


AflutterConfigIdentity = _AflutterConfigIdentity()
