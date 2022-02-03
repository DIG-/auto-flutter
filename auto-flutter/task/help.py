from email import message
from ..core.arguments import Option, Args
from ..core.task import Task, TaskIdentity, TaskResult
from ..core.utils import _Iterable
from ..task._resolver import TaskResolver
from sys import argv as sys_argv
from typing import Dict, List
from ..task.project_read import ProjectRead
from ..core.string_builder import SB


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
        builder = SB()
        self.show_header(builder)
        if "task" in args:
            task_id = args["task"].value
            if (not task_id is None) and len(task_id) > 0:
                identity = TaskResolver.find_task(task_id)
                if not identity is None:
                    self.show_task_options(identity, builder)
                    return TaskResult(args, message=builder.str())
                else:
                    builder.append("Task ").append(task_id, SB.Color.CYAN, True).append(
                        " not found\n"
                    )
        builder.append("Default tasks:\n")
        for task in Help.reduce_indexed_task_into_list(self._default):
            self.show_task_name(task, builder)
        return TaskResult(args, message=builder.str())

    def show_header(self, builder: SB):
        builder.append("Usage:\t").append(sys_argv[0]).append(
            " TASK", SB.Color.CYAN, True
        ).append(" [options]\n", SB.Color.MAGENTA)

    def show_task_options(self, task: TaskIdentity, builder: SB):
        builder.append("\nTask:\t").append(
            task.id, SB.Color.CYAN, True, end="\n"
        ).append(task.name, end="\n")
        options_mapped = map(
            lambda task: task.identity.options, TaskResolver.resolve(task.creator())
        )
        options = _Iterable.flatten(options_mapped)
        if len(options) == 0:
            builder.append("\nThis task does not have options")
        else:
            builder.append("\nOptions:\n")
            for option in options:
                length = 0
                if not option.short is None:
                    builder.append("-" + option.short, SB.Color.MAGENTA)
                    length += len(option.short) + 1
                    if not option.long is None:
                        builder.append(", ")
                        length += 1
                if not option.long is None:
                    builder.append("--" + option.long, SB.Color.MAGENTA)
                    length += len(option.long) + 2
                if option.has_value:
                    builder.append(" <value>", SB.Color.MAGENTA, True)
                    length += 8

                if length < 20:
                    builder.append(" " * (20 - length))
                builder.append("\t").append(option.description, end="\n")

    def show_task_name(self, task: TaskIdentity, builder: SB):
        builder.append("  ").append(task.id, SB.Color.CYAN, True)
        if len(task.id) < 8:
            builder.append(" " * (8 - len(task.id)))
        builder.append("\t").append(task.name, end="\n")

    def reduce_indexed_task_into_list(
        tasks: Dict[str, TaskIdentity]
    ) -> List[TaskIdentity]:
        filtered = filter(lambda it: not it[0].startswith("-"), tasks.items())
        reduced = map(lambda it: it[1], filtered)
        return list(reduced)
