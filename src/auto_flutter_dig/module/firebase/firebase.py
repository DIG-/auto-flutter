from typing import Callable

from ...model.task.identity import TaskIdentity
from ...model.task.subtask import Subtask
from ..plugin import AflutterModulePlugin
from .task.setup.check import FirebaseCheck
from .task.setup.setup import FirebaseSetupTask


class FirebaseModulePlugin(AflutterModulePlugin):
    @property
    def name(self) -> str:
        return "Firebase"

    def register_setup(
        self,
        setup: Subtask,
        check: Callable[[str, TaskIdentity], None],
    ):
        setup.register_subtask(FirebaseSetupTask.identity)
        check("firebase", FirebaseCheck.identity)