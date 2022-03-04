from typing import Dict

from ..model.task import TaskId, TaskIdentity
from ..module.aflutter.task.config.config import AflutterConfigIdentity
from ..module.aflutter.task.project.read import ProjectRead
from ..module.aflutter.task.project.save import ProjectSave
from ..module.aflutter.task.setup import AflutterSetupIdentity
from ..task.help import Help
from .flutter import Flutter
from .flutter.build.config import FlutterBuildConfig
from .flutter.build.stub import FlutterBuildStub
from .flutter.doctor import FlutterDoctor
from .flutter.generator import FlutterGeneratorTask
from .flutter.pub.get import FlutterPubGet
from .project.init import ProjectInit

task_list: Dict[TaskId, TaskIdentity] = dict(
    sorted(
        [
            Help.identity.to_map(),
            AflutterSetupIdentity.to_map(),
            ProjectRead.identity.to_map(),
            ProjectRead.identity_skip.to_map(),
            ProjectInit.identity.to_map(),
            ProjectSave.identity.to_map(),
            Flutter.identity.to_map(),
            FlutterDoctor.to_map(),
            FlutterBuildConfig.identity.to_map(),
            FlutterBuildStub.identity.to_map(),
            AflutterConfigIdentity.to_map(),
            FlutterGeneratorTask.identity.to_map(),
            FlutterGeneratorTask.identity_code.to_map(),
            FlutterPubGet.to_map(),
        ],
        key=lambda x: x[0],
    )
)

user_task: Dict[TaskId, TaskIdentity] = dict()
