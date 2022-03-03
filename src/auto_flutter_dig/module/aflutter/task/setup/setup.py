from .....model.task.subtask import Subtask
from .....module.aflutter.identity import AflutterTaskIdentity
from .....task.base.subtask_parent_task import BaseSubtaskParentTask
from .check import AflutterSetupCheckTask
from .save import AflutterSetupSaveTask
from .show import AflutterSetupShow
from .stack_trace import AflutterSetupStackTraceTask

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
        Subtask.__init__(
            self,
            [
                AflutterSetupShow.identity,
                AflutterSetupSaveTask.identity,
                AflutterSetupStackTraceTask.identity,
                AflutterSetupCheckTask.identity,
            ],
        )


AflutterSetupIdentity = __AflutterSetupIdentity()
