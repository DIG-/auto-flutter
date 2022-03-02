from .....model.error import E, TaskNotFound
from .....model.task import *
from .....model.task.subtask import Subtask
from .....task.project import ProjectRead
from .read_config import ReadConfigTask


class AflutterInitTask(Task):
    def describe(self, args: Args) -> str:
        return "Initialize Aflutter"

    def execute(self, args: Args) -> TaskResult:
        read_config = ReadConfigTask()
        self._uptade_description(read_config.describe(args))
        read_config_result = read_config.execute(args)
        if read_config_result.is_error:
            return read_config_result

        read_project = ProjectRead(warn_if_fail=True)
        self._uptade_description(
            read_project.describe(args),
            read_config_result if read_config_result.is_warning else None,
        )
        read_project_result = read_project.execute(args)
        if read_project_result.is_error:
            return read_project_result

        self._uptade_description(
            "Finding task",
            read_project_result if read_project_result.is_warning else None,
        )

        try:
            raise NotImplementedError("Not implemented yet")
        except TaskNotFound as error:
            raise error
        except BaseException as error:
            return TaskResult(
                args,
                error=E(LookupError("Failed to find task")).caused_by(error),
            )
        return super().execute(args)
