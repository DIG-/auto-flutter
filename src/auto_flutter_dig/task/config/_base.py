from ...model.project import Project  # Will be used by children
from ...model.task import *
from ..identity import AflutterTaskIdentity
from ..options import ParseOptions
from ..project import ProjectRead, ProjectSave

__all__ = [
    "Project",
    "Task",
    "_BaseConfigTask",
    "List",
    "TaskId",
    "TaskIdentity",
    "TaskResult",
    "Option",
    "Args",
    "AflutterTaskIdentity",
]


class _BaseConfigTask(Task):
    def require(self) -> List[TaskId]:
        return [ProjectRead.identity.id, ParseOptions.identity.id]

    def _add_save_project(self):
        self._append_task(ProjectSave())
