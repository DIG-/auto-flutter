from collections import OrderedDict
from typing import Dict
from ..model.task_id import TaskId
from ..core.task import TaskIdentity
from ..task.setup import Setup, SetupEdit
from ..task.help import Help
from ..task.parse_options import ParseOptions
from ..task.project_read import ProjectRead


task_list: Dict[TaskId, TaskIdentity] = OrderedDict(
    dict(
        [
            Help.identity.to_map(),
            SetupEdit.identity.to_map(),
            Setup.identity.to_map(),
            ParseOptions.identity.to_map(),
            ProjectRead.identity.to_map(),
            ProjectRead.identity_skip.to_map(),
        ]
    )
)

user_task: Dict[TaskId, TaskIdentity] = dict()
