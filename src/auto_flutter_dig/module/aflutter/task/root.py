from ....core.utils import _Raise
from ....model.task.group import TaskGroup
from ....module.aflutter.task.config.config import AflutterConfigIdentity
from ....module.aflutter.task.project.init.runner import ProjectInitRunnerTask
from ....module.aflutter.task.project.read import ProjectRead
from ....module.aflutter.task.project.save import ProjectSave
from ....module.aflutter.task.setup import AflutterSetupIdentity
from ..identity import AflutterTaskIdentity
from .help import HelpTask

__all__ = ["Root"]


class _AflutterRoot(AflutterTaskIdentity, TaskGroup):
    def __init__(self) -> None:
        AflutterTaskIdentity.__init__(
            self,
            "-",
            "-",
            [],
            _Raise(AssertionError("Root does not have task")).throw,
            False,
        )
        TaskGroup.__init__(
            self,
            [
                HelpTask.identity,
                ProjectInitRunnerTask.identity,
                AflutterConfigIdentity,
                AflutterSetupIdentity,
                ProjectRead.identity,
                ProjectSave.identity,
            ],
            None,
        )

    def __repr__(self) -> str:
        return "AflutterRoot"


Root = _AflutterRoot()
