from ..plugin import *
from .task.build.stub import FlutterBuildStub
from .task.config.build_param import FlutterBuildParamConfigTask
from .task.exec import FlutterExecTask
from .task.generator import FlutterGeneratorTask
from .task.pub_get import FlutterPubGetIdentity
from .task.setup.check import FlutterSetupCheckTask
from .task.setup.setup import FlutterSetupTask


class FlutterModulePlugin(AflutterModulePlugin):
    @property
    def name(self) -> str:
        return "Flutter"

    def register_setup(
        self,
        setup: TaskGroup,
        check: Callable[[str, TaskIdentity], None],
    ):
        setup.register_subtask(FlutterSetupTask.identity)
        check("flutter", FlutterSetupCheckTask.identity)

    def register_tasks(self, root: TaskGroup):
        root.register_subtask(
            [
                FlutterSetupCheckTask.identity,
                FlutterExecTask.identity,
                FlutterExecTask.doctor,
                FlutterGeneratorTask.identity,
                FlutterGeneratorTask.identity_code,
                FlutterPubGetIdentity,
                FlutterBuildStub.identity,
            ]
        )

    def register_config(self, config: TaskGroup):
        config.register_subtask(
            [
                FlutterBuildParamConfigTask.identity,
            ]
        )
