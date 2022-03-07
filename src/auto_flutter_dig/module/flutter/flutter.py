from ..plugin import *
from .task.config.build_param import FlutterBuildParamConfigTask
from .task.setup.check import FlutterSetupCheckTask
from .task.setup.setup import FlutterSetupTask


class FlutterModulePlugin(AflutterModulePlugin):
    @property
    def name(self) -> str:
        return "Flutter"

    def register_setup(
        self,
        setup: Subtask,
        check: Callable[[str, TaskIdentity], None],
    ):
        setup.register_subtask(FlutterSetupTask.identity)
        check("flutter", FlutterSetupCheckTask.identity)

    def register_tasks(self, root: Subtask):
        root.register_subtask(
            [
                FlutterSetupCheckTask.identity,
            ]
        )

    def register_config(self, config: Subtask):
        config.register_subtask(
            [
                FlutterBuildParamConfigTask.identity,
            ]
        )
