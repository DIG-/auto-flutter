from sys import argv as sys_argv
from typing import List

from ...core.utils import _Iterable
from ...model.task import Task
from ...model.task.help_action import HelpAction
from .firebase import ConfigFirebase
from .flavor import ConfigFlavor
from .platform import ConfigPlatform
from .refresh import ConfigRefresh


class ConfigDispatcher(Task, HelpAction):
    identity = Task.Identity(
        "config", "Configure project", [], lambda: ConfigDispatcher()
    )

    def actions(self) -> List[Task.Identity]:
        return sorted(
            [
                ConfigFlavor.identity,
                ConfigPlatform.identity,
                ConfigRefresh.identity,
                ConfigFirebase.identity,
            ],
            key=lambda x: x.id,
        )

    def execute(self, args: Task.Args) -> Task.Result:
        from ...core.task import TaskManager

        manager = TaskManager

        if len(sys_argv) < 3 or len(sys_argv[2]) <= 0 or sys_argv[2].startswith("-"):
            manager.add(self.__help_task())
            return Task.Result(
                args, error=Warning(" Config task require one action"), success=True
            )

        action = sys_argv[2]
        identity = _Iterable.first_or_none(self.actions(), lambda x: x.id == action)
        if identity is None:
            manager.add(self.__help_task())
            return Task.Result(
                args,
                error=Warning(" Config action `{}` not found".format(action)),
                success=True,
            )

        manager.add(identity.creator())
        return Task.Result(args)

    def __help_task(self) -> Task:
        from ..help import Help

        return Help(self.identity.id)
