from ..core.arguments import Option, Args
from ..core.task import Task, TaskIdentity, TaskResult
from ..core.utils import _Iterable
from ..task._resolver import TaskResolver
from sys import argv as sys_argv
from typing import Dict, List
from ..task.project_read import ProjectRead


class Help(Task):
    identity = TaskIdentity(
        "help",
        "Show help",
        [Option("t", "task", "Show help details about given task", True)],
        lambda: Help(None),
    )

    def __init__(self, default: Dict[str, TaskIdentity]) -> None:
        super().__init__()
        self._default = default

    def describe(self, args: Args) -> str:
        return "Showing help page"

    def require(self) -> List[Task.ID]:
        return [ProjectRead.identity_skip.id]

    def execute(self, args: Args) -> TaskResult:
        self.show_header()
        if "task" in args:
            task_id = args["task"].value
            if (not task_id is None) and len(task_id) > 0:
                identity = TaskResolver.find_task(task_id)
                if not identity is None:
                    self.show_task_options(identity)
                    return TaskResult(args)
                else:
                    self.print('Task "{}" not found\n'.format(task_id))
        self.print("Default tasks:")
        for task in Help.reduce_indexed_task_into_list(self._default):
            self.show_task_name(task)
        return TaskResult(args)

    def show_header(self):
        self.print("Usage:\t{} TASK [options]\n".format(sys_argv[0]))

    def show_task_options(self, task: TaskIdentity):
        self.print("Task:\t{}".format(task.id))
        self.print(task.name)
        options_mapped = map(
            lambda task: task.identity.options, TaskResolver.resolve(task.creator())
        )
        options = _Iterable.flatten(options_mapped)
        if len(options) == 0:
            self.print("\nThis task does not have options")
        else:
            self.print("\nOptions:")
            for option in options:
                has_value = " <value>" if option.has_value else ""
                separator = (
                    ", "
                    if (not option.short is None) and (not option.long is None)
                    else ""
                )
                has_short = "-" + option.short if not option.short is None else ""
                has_long = "--" + option.long if not option.long is None else ""
                final = has_short + separator + has_long + has_value
                self.print("{:20s}\t{}".format(final, option.description))

    def show_task_name(self, task: TaskIdentity):
        self.print("  {}\t{}".format(task.id, task.name))

    def reduce_indexed_task_into_list(
        tasks: Dict[str, TaskIdentity]
    ) -> List[TaskIdentity]:
        filtered = filter(lambda it: not it[0].startswith("-"), tasks.items())
        reduced = map(lambda it: it[1], filtered)
        return list(reduced)
