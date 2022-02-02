from typing import Deque
from termcolor import colored
from ..core.task import Task
from ..core.arguments import Args
from ..core.task_printer import TaskPrinter
from ..task._list import task_list
from ..task._resolver import TaskResolver
from ..task.help import Help
from ..task.parse_options import ParseOptions


class TaskManager:
    __instance: "TaskManager" = None

    def instance() -> "TaskManager":
        if TaskManager.__instance is None:
            TaskManager.__instance = TaskManager()
        return TaskManager.__instance

    def __init__(self) -> None:
        self._task_stack: Deque[Task] = Deque()
        self._printer = TaskPrinter()

    def add(self, task: Task):
        if type(task) is Help:
            task = Help(task_list)
        self._task_stack = TaskResolver.resolve(task)

    def add_id(self, task_id: Task.ID):
        identity = TaskResolver.find_task(task_id)
        if identity is None:
            raise LookupError("Task " + colored(task_id, "magenta") + " not found")
        self.add(identity.creator())

    def print(self, message: str):
        self._printer.write(message)

    def execute(self) -> bool:
        args = Args()
        self._printer.start()
        self._task_stack.append(ParseOptions(self._task_stack))
        while len(self._task_stack) > 0:
            current = self._task_stack.pop()
            describe = current.describe(args)
            if (not describe is None) and len(describe) != 0:
                self._printer.set_task_description(describe)
            output = current.execute(args)
            self._printer.set_result(output)
            if not output.success:
                self._printer.stop()
                return False
            args = output.args
        self._printer.stop()
        return True
