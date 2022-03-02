from ...core.string import SB
from ...core.utils import _Ensure
from ...model.error import SilentWarning
from ...model.task import *
from ...model.task.subtask import Subtask
from ...task.help import Help

__all__ = ["BaseSubtaskParentTask"]


class BaseSubtaskParentTask(Task):
    def __init__(self, identity: TaskIdentity, subtask: Subtask) -> None:
        super().__init__()
        self.identity = _Ensure.instance(identity, TaskIdentity, "identity")
        self._subtask: Subtask = _Ensure.instance(subtask, Subtask, "subtask")

    def describe(self, args: Args) -> str:
        # Basically will show help for subtasks
        return ""

    def execute(self, args: Args) -> TaskResult:
        self._append_task(
            Help.Stub(
                self.identity,
                SB()
                .append("Task ", SB.Color.YELLOW)
                .append(self.identity.id, SB.Color.CYAN)
                .append(" require subtask!", SB.Color.YELLOW)
                .str(),
            )
        )
        return TaskResult(args, SilentWarning("Task require subtask"), success=True)
