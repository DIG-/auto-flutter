from sys import argv as sys_argv
from typing import Optional, Tuple

from .....model.error import E, SilentWarning, TaskNotFound
from .....model.task import *
from .....model.task.subtask import Subtask
from .....module.aflutter.task.root import Root
from .....task.help import Help
from .....task.options import ParseOptions
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
            task, offset = self.__find_task(Root)
        except TaskNotFound as error:
            self._append_task(Help.Stub(error.task_id))
            return TaskResult(args, E(SilentWarning()).caused_by(error), success=True)
        except BaseException as error:
            return TaskResult(
                args,
                error=E(LookupError("Failed to find task")).caused_by(error),
            )

        try:
            self._append_task(task)
        except BaseException as error:
            return TaskResult(
                args,
                error=E(RuntimeError("Failed to create task tree")).caused_by(error),
            )

        parse_options = ParseOptions(sys_argv[offset:])
        self._uptade_description(parse_options.describe(args))
        parse_options_result = parse_options.execute(args)
        return parse_options_result

    def __find_task(self, root: Subtask) -> Tuple[TaskIdentity, int]:
        task: Optional[TaskIdentity] = None
        offset = 1
        limit = len(sys_argv)
        while offset < limit:
            task_id = sys_argv[offset]
            if task_id.startswith("-"):
                break
            if not task_id in root.subtasks:
                break
            task = root.subtasks[task_id]
            offset += 1
            if isinstance(task, Subtask):
                root = task
            else:
                break
            pass

        if not task is None:
            return (task, offset)
        raise TaskNotFound(task_id)
