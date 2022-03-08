from ......model.argument.option import LongOptionWithValue, LongShortOption
from ......model.task import *
from ......model.task.init.project_identity import InitProjectTaskIdentity
from ....identity import AflutterTaskIdentity


class ProjectInitRunnerTask(Task):
    __opt_name = LongOptionWithValue("name", "Name of project")
    __opt_force = LongShortOption("f", "force", "Ignore existing project file")
    identity = AflutterTaskIdentity(
        "init",
        "Initialize Auto-Flutter project",
        [__opt_name, __opt_force],
        lambda: ProjectInitRunnerTask(),  # pylint: disable=unnecessary-lambda
    )
    external_tasks: List[InitProjectTaskIdentity] = []

    def describe(self, args: Args) -> str:
        return "Prepare to init project"

    def execute(self, args: Args) -> TaskResult:
        raise NotImplementedError("Not implemented yet")
