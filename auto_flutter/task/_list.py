from collections import OrderedDict
from typing import Dict

from ..model.task import TaskId, TaskIdentity
from ..task.build import FlutterBuild
from ..task.flutter import Flutter, FlutterDoctor
from ..task.help import Help
from ..task.parse_options import ParseOptions
from ..task.project_read import ProjectRead
from ..task.setup import Setup, SetupEdit

task_list: Dict[TaskId, TaskIdentity] = OrderedDict(
    dict(
        [
            Help.identity.to_map(),
            SetupEdit.identity.to_map(),
            Setup.identity.to_map(),
            ParseOptions.identity.to_map(),
            ProjectRead.identity.to_map(),
            ProjectRead.identity_skip.to_map(),
            Flutter.identity.to_map(),
            FlutterDoctor.to_map(),
            FlutterBuild.identity.to_map(),
        ]
    )
)

user_task: Dict[TaskId, TaskIdentity] = dict()
