from __future__ import annotations

from typing import Optional

from ..task import TaskId
from ..task.subtask import Subtask


class TaskNotFound(LookupError):
    def __init__(self, task_id: TaskId, parent: Subtask, *args: object) -> None:
        super().__init__(*args)
        self.task_id: TaskId = task_id
        self.parent: Subtask = parent
