from pathlib import Path
from sys import argv as sys_argv
from typing import Dict, Iterable, List, Optional, Union

from ....core.string import SB
from ....core.task import TaskResolver
from ....core.utils import _Iterable
from ....model.argument.option import *
from ....model.error import E, TaskNotFound
from ....model.task import *
from ....model.task.group import TaskGroup
from ..identity import AflutterTaskIdentity


class HelpTask(Task):
    class Stub(AflutterTaskIdentity):
        def __init__(
            self,
            task_id: Optional[Union[TaskId, TaskIdentity, TaskNotFound]] = None,
            message: Optional[str] = None,
        ) -> None:
            super().__init__(
                HelpTask.identity.id,
                HelpTask.identity.name,
                HelpTask.identity.options,
                lambda: HelpTask(task_id, message),
                HelpTask.identity.allow_more,
            )

    option_task = LongPositionalOption("task", 0, "Show help details about given task")

    identity = AflutterTaskIdentity(
        "help",
        "Show help",
        [option_task],
        lambda: HelpTask(None, None),
    )

    def __init__(
        self,
        task_id: Optional[Union[TaskId, TaskIdentity, TaskNotFound]] = None,
        message: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._task_id: Optional[TaskId] = None
        self._task_identity: Optional[TaskIdentity] = None
        self._task_parent: Optional[TaskGroup] = None
        self._message: Optional[str] = message
        if isinstance(task_id, TaskIdentity):
            self._task_identity = task_id
            self._task_parent = task_id.parent
        elif isinstance(task_id, TaskId):
            self._task_id = task_id
        elif isinstance(task_id, TaskNotFound):
            self._task_id = task_id.task_id
            self._task_parent = task_id.parent
        elif not task_id is None:
            raise TypeError(
                "Field `task_id` must be instance of `TaskId`, `TaskIdentity` or `TaskNotFound`,"
                + f" but `{type(task_id)}` was used"
            )

    def describe(self, args: Args) -> str:
        return "Processing help page"

    def execute(self, args: Args) -> TaskResult:
        builder = SB()
        opt_task_id = args.get(self.option_task)
        if not opt_task_id is None:
            self._task_id = opt_task_id
            self._task_parent = None

        if self._task_parent is None:
            from .root import Root

            self._task_parent = Root

        assert not self._task_parent is None
        positional_options: Iterable[PositionalOption] = []
        options: Iterable[Option] = []

        if (
            self._task_identity is None
            and (not self._task_id is None)
            and (len(self._task_id) > 0)
            and (not self._task_id.startswith("-"))
        ):
            try:
                self._task_identity = TaskResolver.find_task(self._task_id, self._task_parent)
            except TaskNotFound:
                pass
            except BaseException as error:
                return TaskResult(
                    args,
                    error=E(LookupError(f"Failed to search for task {self._task_id}.")).caused_by(error),
                )
            pass

        if not self._task_identity is None:
            task_parent = self._task_identity.parent
            if task_parent is None:
                task_parent = self._task_parent
            options_mapped = map(
                lambda r_identity: r_identity.options,
                TaskResolver.resolve(self._task_identity, origin=task_parent),
            )
            options = _Iterable.flatten(options_mapped)
            positional_options = sorted(
                _Iterable.is_instance(options, PositionalOption),
                key=lambda x: x.position,
            )

        if not self._message is None:
            builder.append(self._message, end="\n")

        self._show_header(builder, self._task_identity, positional_options)

        if not self._task_identity is None:
            task_parent = self._task_identity.parent
            if task_parent is None:
                task_parent = self._task_parent
            self._show_task_help(builder, self._task_identity, task_parent, options)
        elif not self._task_id is None:
            builder.append(" !!! ", SB.Color.RED).append("Task ").append(self._task_id, SB.Color.CYAN, True).append(
                " not found\n"
            )
            self._show_help_default(builder, self._task_parent)
        else:
            self._show_help_default(builder, self._task_parent)

        self._uptade_description("Showing help page")
        return TaskResult(args, message=builder.str())

    def _show_help_default(self, builder: SB, root: TaskGroup):
        self._show_help_grouped(builder, self._grouped_tasks(root))

    def _show_header(
        self,
        builder: SB,
        identity: Optional[TaskIdentity],
        positional: Iterable[PositionalOption],
    ):
        from .root import Root

        program = Path(sys_argv[0]).name
        if program == "__main__.py":
            program = "python -m auto_flutter_dig"
        builder.append("\nUsage:\t").append(program, end=" ")

        tasks: List[str] = []
        t_identity = identity
        while not t_identity is None:
            if t_identity != Root:
                tasks.append(t_identity.id)
            parent = t_identity.parent
            if isinstance(parent, TaskIdentity):
                t_identity = parent
            else:
                t_identity = None
        if len(tasks) > 0:
            tasks.reverse()
            builder.append(" ".join(tasks), SB.Color.CYAN, True, end=" ")

        if isinstance(identity, TaskGroup) or identity is None:
            builder.append("TASK ", SB.Color.CYAN, True)

        for pos in positional:
            builder.append("{", SB.Color.MAGENTA, True).append(pos.name, SB.Color.MAGENTA, True).append(
                "} ", SB.Color.MAGENTA, True
            )
        builder.append("[options]\n", SB.Color.MAGENTA)

    def _show_task_description(self, builder: SB, identity: TaskIdentity):
        builder.append("\nTask:\t").append(identity.id, SB.Color.CYAN, True, end="\n").append(identity.name, end="\n")
        pass

    def _show_task_help(
        self,
        builder: SB,
        identity: TaskIdentity,
        root: TaskGroup,
        options: Iterable[Option],
    ):
        self._show_task_description(builder, identity)
        if isinstance(identity, TaskGroup):
            self._show_help_grouped(builder, self._grouped_tasks(identity))

        builder.append("\nOptions:\n")
        self._show_task_options(builder, options)

    def _show_task_identity_description(self, builder: SB, identity: TaskIdentity):
        builder.append("  ").append(identity.id, SB.Color.CYAN, True)
        if len(identity.id) < 8:
            builder.append(" " * (8 - len(identity.id)))
        builder.append("\t").append(identity.name, end="\n")

    def _show_task_options(self, builder: SB, options: Iterable[Option]):
        count = 0
        for option in options:
            count += 1
            length = 0
            if isinstance(option, ShortOption):
                builder.append("-" + option.short, SB.Color.MAGENTA)
                length += len(option.short) + 1

            if isinstance(option, LongOption):
                if length != 0:
                    builder.append(", ")
                    length += 2
                builder.append("--" + option.long, SB.Color.MAGENTA)
                length += len(option.long) + 2

            if isinstance(option, OptionWithValue):
                builder.append(" <value>", SB.Color.MAGENTA, True)
                length += 8

            if length < 20:
                builder.append(" " * (20 - length))
            builder.append("\t").append(option.description, end="\n")

        if count == 0:
            builder.append("This task does not have options")

    def _show_help_grouped(self, builder: SB, grouped: Dict[str, List[TaskIdentity]]):
        for group, identities in grouped.items():
            builder.append("\n")
            self._show_help_by_group(builder, group, identities)
        pass

    def _show_help_by_group(
        self,
        builder: SB,
        group: str,
        identities: List[TaskIdentity],
    ):
        builder.append("Tasks for ").append(group, SB.Color.CYAN).append(":\n")
        for identity in identities:
            self._show_task_identity_description(builder, identity)
        pass

    @staticmethod
    def reduce_indexed_task_into_list(tasks: Dict[str, TaskIdentity]) -> List[TaskIdentity]:
        filtered = filter(lambda it: not it[0].startswith("-"), tasks.items())
        reduced = map(lambda it: it[1], filtered)
        return list(reduced)

    def _grouped_tasks(self, root: TaskGroup) -> Dict[str, List[TaskIdentity]]:
        output: Dict[str, List[TaskIdentity]] = {}
        for group in sorted(map(lambda x: x[1].group, root.subtasks.items())):
            if not group in output:
                output[group] = []
        for _, identity in root.subtasks.items():
            if not identity.group in output:
                output[identity.group] = []
            output[identity.group].append(identity)
        for group, identities in output.copy().items():
            output[group] = list(filter(lambda x: not x.id.startswith("-"), identities))
            if len(output[group]) == 0:
                output.pop(group)
        return output
