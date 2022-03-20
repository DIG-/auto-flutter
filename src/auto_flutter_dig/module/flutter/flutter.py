from ...module.flutter.task.build.stub import FlutterBuildStub
from ...module.flutter.task.config.build_param import FlutterBuildParamConfigTask
from ...module.flutter.task.exec import FlutterExecTask
from ...module.flutter.task.generator import FlutterGeneratorTask
from ...module.flutter.task.pub_get import FlutterPubGetIdentity
from ...module.flutter.task.setup.check import FlutterSetupCheckTask
from ...module.flutter.task.setup.setup import FlutterSetupTask
from ...module.plugin import *


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
