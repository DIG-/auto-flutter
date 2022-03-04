from .....model.task import *
from .....model.task.subtask import Subtask
from .....task.base.subtask_parent_task import BaseSubtaskParentTask
from ...identity import AflutterTaskIdentity

__all__ = ["AflutterConfigIdentity"]


class __AflutterConfigIdentity(AflutterTaskIdentity, Subtask):
    def __init__(self) -> None:
        AflutterTaskIdentity.__init__(
            self,
            "config",
            "Configure project",
            [],
            lambda: BaseSubtaskParentTask(self, self),
        )
        Subtask.__init__(self, [])


AflutterConfigIdentity = __AflutterConfigIdentity()