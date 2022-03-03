from typing import Callable

from ...model.task.identity import TaskIdentity
from ...model.task.subtask import Subtask
from ..plugin import AflutterModulePlugin
from .task.setup.check import FirebaseCheck


class FirebaseModulePlugin(AflutterModulePlugin):
    @property
    def name(self) -> str:
        return "Firebase"

    def register_setup(
        self,
        setup: Subtask,
        check: Callable[[str, TaskIdentity], None],
    ):
        check("firebase", FirebaseCheck.identity)
