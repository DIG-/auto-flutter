from ...core.string.builder import SB
from ...model.project import Project
from ...model.project.custom_task import CustomTask, CustomTaskType
from ...model.task import *
from ...model.task.custom import *


class ProjectTaskImport(Task):
    def describe(self, args: Args) -> str:
        return "Importing project tasks"

    def execute(self, args: Args) -> TaskResult:
        project = Project.current
        if project.tasks is None:
            return TaskResult(
                args,
                AssertionError("Unexpected run while project has no custom task"),
                success=True,
            )
        for custom in project.tasks:
            if custom.type == CustomTaskType.EXEC:
                self.__add_custom_task(CustomExecIdentity(custom))
            else:
                self._print(
                    SB()
                    .append("Not implemented custom task type ", SB.Color.YELLOW)
                    .append(str(custom.type), SB.Color.CYAN)
                    .str()
                )

        self.__sort_custom_task()
        return TaskResult(args)

    def __add_custom_task(self, identity: TaskIdentity):
        from .._list import task_list, user_task

        if identity.id in task_list:
            raise KeyError("CustomTask can not override internal task")
        user_task[identity.id] = identity

    def __sort_custom_task(self):
        pass
