from typing import List

from ...model.project import Project  # Will be used by children
from ...model.task import Task
from ..options import ParseOptions
from ..project import ProjectRead, ProjectSave

__all__ = ["Project", "Task", "_BaseConfigTask"]


class _BaseConfigTask(Task):
    def require(self) -> List[Task.ID]:

        return [ProjectRead.identity.id, ParseOptions.identity.id]

    def _add_save_project(self):
        from ...core.task import TaskManager

        TaskManager.instance().add(ProjectSave())
