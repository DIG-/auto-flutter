from typing import Dict, Final

from ..model.task import TaskId, TaskIdentity
from ..task.help import Help
from ..task.parse_options import ParseOptions
from .firebase import FirebaseCheck
from .flutter import Flutter
from .flutter.build.config import FlutterBuildConfig
from .flutter.doctor import FlutterDoctor
from .project.init import ProjectInit
from .project.read import ProjectRead
from .project.save import ProjectSave
from .setup import Setup, SetupEdit

task_list: Final[Dict[TaskId, TaskIdentity]] = dict(
    sorted(
        [
            Help.identity.to_map(),
            SetupEdit.identity.to_map(),
            Setup.identity.to_map(),
            ParseOptions.identity.to_map(),
            ProjectRead.identity.to_map(),
            ProjectRead.identity_skip.to_map(),
            ProjectInit.identity.to_map(),
            ProjectSave.identity.to_map(),
            Flutter.identity.to_map(),
            FlutterDoctor.to_map(),
            FlutterBuildConfig.identity.to_map(),
            FirebaseCheck.identity.to_map(),
        ],
        key=lambda x: x[0],
    )
)

user_task: Dict[TaskId, TaskIdentity] = dict()
