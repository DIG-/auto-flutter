from .....model.task import Task
from .....model.task.subtask import Subtask
from .....module.aflutter.identity import AflutterTaskIdentity
from .....task.base.subtask_parent_task import BaseSubtaskParentTask

__all__ = ["AflutterSetupIdentity"]


class __AflutterSetupIdentity(AflutterTaskIdentity, Subtask):
    def __init__(self) -> None:
        AflutterTaskIdentity.__init__(
            self,
            "setup",
            "Configure environment",
            [],
            lambda: BaseSubtaskParentTask(self, self),
        )
        Subtask.__init__(self, [])


AflutterSetupIdentity = __AflutterSetupIdentity()
