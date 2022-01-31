from typing import Dict
from core.task import TaskIdentity
from task.setup import Setup


task_list: Dict[str, TaskIdentity] = dict(
    [
        Setup.identity.to_map(),
    ]
)
