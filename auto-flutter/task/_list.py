from typing import Dict
from ..core.task import TaskIdentity
from ..task.setup import Setup
from ..task.help import Help


task_list: Dict[str, TaskIdentity] = dict(
    [
        Help.identity.to_map(),
        Setup.identity.to_map(),
    ]
)

user_task: Dict[str, TaskIdentity] = dict()
