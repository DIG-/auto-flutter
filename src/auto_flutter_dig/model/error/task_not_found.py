from __future__ import annotations

from ..task.group import TaskGroup
from ..task.id import TaskId


class TaskNotFound(LookupError):
    def __init__(self, task_id: TaskId, parent: TaskGroup, *args: object) -> None:
        super().__init__(*args)
        self.task_id: TaskId = task_id
        self.parent: TaskGroup = parent
