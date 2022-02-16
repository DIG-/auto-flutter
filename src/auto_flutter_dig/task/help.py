from pathlib import Path
from sys import argv as sys_argv
from typing import Dict, List, Optional, Union

from ..core.string import SB
from ..core.task import TaskResolver
from ..core.utils import _Ensure, _If, _Iterable
from ..model.task import *
from ..model.task.help_action import HelpAction
from .options import ParseOptions
from .project.read import ProjectRead


class Help(Task):
    option_task = Option("t", "task", "Show help details about given task", True)

    identity = TaskIdentity(
        "help",
        "Show help",
        [option_task],
        lambda: Help(),
    )

    def __init__(
        self,
        task_id: Optional[Union[TaskId, TaskIdentity]] = None,
        message: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._show_task: Optional[TaskId] = None
        self._message: Optional[str] = message
        if isinstance(task_id, TaskIdentity):
            self._show_task = task_id.id
        elif isinstance(task_id, TaskId):
            self._show_task = task_id
        elif not task_id is None:
            raise TypeError(
                "Field `task_id` must be instance of `{clsa}` or `{clsb}`, but `{input}` was used".format(
                    clsa=TaskId.__name__,
                    clsb=TaskIdentity.__name__,
                    input=type(task_id),
                )
            )

    def describe(self, args: Args) -> str:
        return "Showing help page"

    def require(self) -> List[TaskId]:
        if self._show_task is None:
            return [ParseOptions.identity.id, ProjectRead.identity_skip.id]
        return [ProjectRead.identity_skip.id]

    def execute(self, args: Args) -> TaskResult:
        builder = SB()
        task_name = args.get_value(self.option_task)
        if not self._show_task is None:
            task_name = self._show_task
        task_not_found = False
        if (
            (not task_name is None)
            and (len(task_name) > 0)
            and (not task_name.startswith("-"))
        ):
            identity = TaskResolver.find_task(task_name)
            task_instance: Optional[Task] = _If.not_none(
                identity, lambda x: x.creator(), lambda: None
            )
            if identity is None:
                task_not_found = True
            elif isinstance(task_instance, HelpAction):
                self._show_task_help_with_actions(builder, identity, task_instance)
                return TaskResult(args, message=builder.str())
            else:
                self._show_task_help(builder, identity)
                return TaskResult(args, message=builder.str())

        if not self._message is None:
            builder.append(self._message, end="\n")

        self._show_header(builder)

        if task_not_found:
            assert not task_name is None
            builder.append(" !!! ", SB.Color.RED).append("Task ").append(
                task_name, SB.Color.CYAN, True
            ).append(" not found\n")

        builder.append("\nCommon options:\n")
        self._show_task_options(builder, ParseOptions.identity.options, False)

        builder.append("\nDefault tasks:\n")
        from ..task._list import task_list, user_task

        for identity in Help.reduce_indexed_task_into_list(task_list):
            self._show_task_name_description(builder, identity)

        user_reduced = Help.reduce_indexed_task_into_list(user_task)
        if len(user_reduced) <= 0:
            return TaskResult(args, message=builder.str())

        builder.append("\nUser tasks:\n")
        for identity in user_reduced:
            self._show_task_name_description(builder, identity)
        return TaskResult(args, message=builder.str())

    def _show_header(self, builder: SB, has_action: bool = False):
        program = Path(sys_argv[0]).name
        if program == "__main__.py":
            program = "python -m auto_flutter_dig"
        builder.append("\nUsage:\t").append(program, end=" ").append(
            "TASK ACTION" if has_action else "TASK", SB.Color.CYAN, True
        ).append(" [options]\n", SB.Color.MAGENTA)

    def _show_task_description(self, builder: SB, identity: TaskIdentity):
        builder.append("\nTask:\t").append(
            identity.id, SB.Color.CYAN, True, end="\n"
        ).append(identity.name, end="\n")
        pass

    def _show_task_help(self, builder: SB, identity: TaskIdentity):
        self._show_header(builder)
        self._show_task_description(builder, identity)
        options_mapped = map(
            lambda r_identity: filter(lambda x: not x.hidden, r_identity.options),
            TaskResolver.resolve(identity),
        )
        options = _Iterable.flatten(options_mapped)
        builder.append("\nOptions:\n")
        self._show_task_options(builder, options)

    def _show_task_name_description(self, builder: SB, identity: TaskIdentity):
        builder.append("  ").append(identity.id, SB.Color.CYAN, True)
        if len(identity.id) < 8:
            builder.append(" " * (8 - len(identity.id)))
        builder.append("\t").append(identity.name, end="\n")

    def _show_task_options(
        self, builder: SB, options: List[Option], is_action: bool = False
    ):
        if len(options) <= 0:
            if is_action:
                builder.append("This action does not have options")
            else:
                builder.append("This task does not have options")
            return
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
        pass

    def _show_task_help_with_actions(
        self, builder: SB, identity: TaskIdentity, task: Task
    ):
        helper = task
        if not isinstance(helper, HelpAction):
            raise TypeError(
                "Field `{name}` must be instance of `{cls}`, but `{input}` was used".format(
                    name="helper",
                    cls=HelpAction.__name__,
                    input=_Ensure.name(type(helper)),
                )
            )
        self._show_header(builder, True)
        self._show_task_description(builder, identity)
        builder.append("\nActions:\n")
        for action in helper.actions():
            self._show_task_actions(builder, action, action.creator())
            pass
        pass

    def _show_task_actions(self, builder: SB, identity: TaskIdentity, task: Task):
        self._show_task_name_description(builder, identity)
        options: List[Option] = _Iterable.flatten(
            map(
                lambda r_identity: r_identity.options,
                TaskResolver.resolve(task),
            )
        )
        self._show_task_options(builder, options)
        pass

    @staticmethod
    def reduce_indexed_task_into_list(
        tasks: Dict[str, TaskIdentity]
    ) -> List[TaskIdentity]:
        filtered = filter(lambda it: not it[0].startswith("-"), tasks.items())
        reduced = map(lambda it: it[1], filtered)
        return list(reduced)
