from typing import Callable

from ...model.task.identity import TaskIdentity
from ...model.task.group import TaskGroup
from ..plugin import AflutterModulePlugin
from .task.config import FirebaseConfigTask
from .task.setup.check import FirebaseCheck
from .task.setup.setup import FirebaseSetupTask
from .task.upload import FirebaseBuildUpload
from .task.validate import FirebaseBuildValidate


class FirebaseModulePlugin(AflutterModulePlugin):
    @property
    def name(self) -> str:
        return "Firebase"

    def register_setup(
        self,
        setup: TaskGroup,
        check: Callable[[str, TaskIdentity], None],
    ):
        setup.register_subtask(FirebaseSetupTask.identity)
        check("firebase", FirebaseCheck.identity)

    def register_config(self, config: TaskGroup):
        config.register_subtask(FirebaseConfigTask.identity)

    def register_tasks(self, root: TaskGroup):
        root.register_subtask(
            [
                FirebaseBuildUpload.identity,
                FirebaseBuildValidate.identity,
                FirebaseCheck.identity,
            ]
        )
