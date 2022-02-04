from ..core.arguments import Option, Args
from ..core.task import Task, TaskIdentity, TaskResult
from ..core.utils import _Iterable
from ..task._resolver import TaskResolver
from sys import argv as sys_argv
from typing import Dict, List, Optional
from ..task.project_read import ProjectRead
from ..core.string_builder import SB


class Help(Task):
    identity = TaskIdentity(
        "help",
        "Show help",
        [Option("t", "task", "Show help details about given task", True)],
        lambda: Help(),
    )

    def __init__(self) -> None:
        super().__init__()

    def describe(self, args: Args) -> str:
        return "Showing help page"

    def require(self) -> List[Task.ID]:
        return [ProjectRead.identity_skip.id]

    def execute(self, args: Args) -> TaskResult:
        builder = SB()
        self.show_header(builder)
        if "task" in args:
            if self._show_help_for_task_id(builder, args["task"].value):
                return TaskResult(args, message=builder.str())

        builder.append("\nDefault tasks:\n")
        from ..task._list import task_list, user_task

        for task in Help.reduce_indexed_task_into_list(task_list):
            self.show_task_name(task, builder)

        user_reduced = Help.reduce_indexed_task_into_list(user_task)
        if len(user_reduced) <= 0:
            return TaskResult(args, message=builder.str())

        builder.append("\nUser tasks:\n")
        for task in user_reduced:
            self.show_task_name(task, builder)

    def show_header(self, builder: SB):
        builder.append("Usage:\t").append(sys_argv[0]).append(
            " TASK", SB.Color.CYAN, True
        ).append(" [options]\n", SB.Color.MAGENTA)

    def _show_help_for_task_id(self, builder: SB, id: Optional[str]) -> bool:
        if id is None or len(id) <= 0:
            return False
        if id.startswith("-"):
            identity = None
        else:
            identity = TaskResolver.find_task(id)
        if identity is None:
            builder.append("Task ").append(id, SB.Color.CYAN, True).append(
                " not found\n"
            )
            return False

        self._show_task_options(identity, builder)
        return True

    def _show_task_options(self, task: TaskIdentity, builder: SB):
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