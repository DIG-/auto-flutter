from ...core.utils import _Raise
from ...model.task.subtask import Subtask
from ...task._list import task_list
from ...task.identity.aflutter import AflutterTaskIdentity

__all__ = ["Root"]


class __AflutterRoot(AflutterTaskIdentity, Subtask):
    def __init__(self) -> None:
        AflutterTaskIdentity.__init__(
            self,
            "-",
            "-",
            [],
            _Raise(AssertionError("Root does not have task")).throw,
            False,
        )
        Subtask.__init__(self, task_list, None)

    def __repr__(self) -> str:
        return "AflutterRoot"


Root = __AflutterRoot()
