from .....core.utils.task.subtask_parent_task import BaseSubtaskParentTask
from .....model.task.group import TaskGroup
from .....module.aflutter.identity import AflutterTaskIdentity
from .check import AflutterSetupCheckTask
from .save import AflutterSetupSaveTask
from .show import AflutterSetupShow
from .stack_trace import AflutterSetupStackTraceTask

__all__ = ["AflutterSetupIdentity"]


class __AflutterSetupIdentity(AflutterTaskIdentity, TaskGroup):
    def __init__(self) -> None:
        AflutterTaskIdentity.__init__(
            self,
            "setup",
            "Configure environment",
            [],
            lambda: BaseSubtaskParentTask(self, self),
        )
        TaskGroup.__init__(
            self,
            [
                AflutterSetupShow.identity,
                AflutterSetupSaveTask.identity,
                AflutterSetupStackTraceTask.identity,
                AflutterSetupCheckTask.identity,
            ],
        )


AflutterSetupIdentity = __AflutterSetupIdentity()
