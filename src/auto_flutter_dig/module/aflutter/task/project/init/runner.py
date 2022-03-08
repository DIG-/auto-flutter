from ......model.task import *
from ......model.task.init.project_identity import InitProjectTaskIdentity
from ....identity import AflutterTaskIdentity
from .create import ProjectInitCreateTask


class ProjectInitRunnerTask(Task):

    identity = AflutterTaskIdentity(
        "init",
        "Initialize Auto-Flutter project",
        [ProjectInitCreateTask.opt_name, ProjectInitCreateTask.opt_force],
        lambda: ProjectInitRunnerTask(),  # pylint: disable=unnecessary-lambda
    )
    external_tasks: List[InitProjectTaskIdentity] = []

    def describe(self, args: Args) -> str:
        return "Prepare to init project"

    def execute(self, args: Args) -> TaskResult:
        tasks: List[TaskIdentity] = [ProjectInitCreateTask.identity]
        self._append_task(tasks)
        return TaskResult(args)
