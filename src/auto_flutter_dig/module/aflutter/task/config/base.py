from .....model.project.project import Project
from .....model.task.task import *
from ..project.read import ProjectRead
from ..project.save import ProjectSave

__all__ = [
    "Project",
    "Task",
    "BaseConfigTask",
    "List",
    "TaskId",
    "TaskResult",
    "Args",
]


class BaseConfigTask(Task):
    def require(self) -> List[TaskId]:
        return [ProjectRead.identity.task_id]

    def _add_save_project(self):
        self._append_task(ProjectSave.identity)
