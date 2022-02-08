from typing import List

from ...model.task import Task
from ...model.task.help_action import HelpAction


class ConfigDispatcher(Task, HelpAction):
    identity = Task.Identity(
        "config", "Configure project", [], lambda: ConfigDispatcher()
    )

    def describe(self, args: Task.Args) -> str:
        return ""

    def actions(self) -> List[Task.Identity]:
        return []

    def execute(self, args: Task.Args) -> Task.Result:
        return Task.Result(args, error=NotImplementedError())
