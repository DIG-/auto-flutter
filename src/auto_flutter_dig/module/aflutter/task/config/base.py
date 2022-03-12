from .....model.project import Project
from .....model.task import *
from ..project.read import ProjectRead
from ..project.save import ProjectSave

__all__ = [
    "Project",
    "Task",
    "BaseConfigTask",
    "List",
    "TaskId",
    "TaskIdentity",
    "TaskResult",
    "Args",
    "E",
]


class BaseConfigTask(Task):
    def require(self) -> List[TaskId]:
        return [ProjectRead.identity.id]

    def _add_save_project(self):
        self._append_task(ProjectSave.identity)
