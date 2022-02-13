from auto_flutter.core.string.builder import SB

from ...core.utils import _Dict
from ...model.project import Project
from ...model.project.custom_task import CustomTask
from ...model.task import Task
from ...model.task.custom import *


class ProjectTaskImport(Task):
    def describe(self, args: Task.Args) -> str:
        return "Importing project tasks"

    def execute(self, args: Task.Args) -> Task.Result:
        project = Project.current
        if project.tasks is None:
            return Task.Result(
                args,
                AssertionError("Unexpected run while project has no custom task"),
                success=True,
            )
        for custom in project.tasks:
            if custom.type == CustomTask.Type.EXEC:
                self.__add_custom_task(CustomExecIdentity(custom))
            else:
                self._print(
                    SB()
                    .append("Not implemented custom task type ", SB.Color.YELLOW)
                    .append(str(custom.type), SB.Color.CYAN)
                    .str()
                )

        self.__sort_custom_task()
        return Task.Result(args)

    def __add_custom_task(self, identity: Task.Identity):
        from .._list import task_list, user_task

        if identity.id in task_list:
            raise KeyError("CustomTask can not override internal task")
        user_task[identity.id] = identity

    def __sort_custom_task(self):
        pass
