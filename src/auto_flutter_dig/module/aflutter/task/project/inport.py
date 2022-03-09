from .....core.string.builder import SB
from .....model.project import Project
from .....model.project.custom_task import CustomTaskType
from .....model.result import Result
from .....model.task import *
from .....module.user.task.exec import UserExecTaskIdentity


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
        tasks: List[TaskIdentity] = []
        for custom in project.tasks:
            if custom.type == CustomTaskType.EXEC:
                if custom.content is None:
                    self._reset_description(args, Result(E(ValueError("User task type EXEC require content")).error))
                    continue
                if custom.content.args is None or len(custom.content.args) <= 0:
                    self._reset_description(
                        args, Result(E(ValueError("User task type EXEC require content arguments")).error)
                    )
                    continue
                tasks.append(UserExecTaskIdentity(custom.id, custom.name, custom.content.args))
            else:
                self._print(
                    SB()
                    .append("Not implemented custom task type ", SB.Color.YELLOW)
                    .append(str(custom.type), SB.Color.CYAN)
                    .str()
                )
        if len(tasks) > 0:
            from .....module.aflutter.task.root import Root  # pylint:disable=import-outside-toplevel

            for identity in tasks:
                if identity.id in Root.subtasks:
                    raise KeyError("UserTask can not override internal task")
            Root.register_subtask(tasks)

        return TaskResult(args)
