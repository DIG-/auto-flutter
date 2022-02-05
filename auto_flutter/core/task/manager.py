from __future__ import annotations

from typing import Deque

from ...model.task import Task
from ...task._resolver import TaskResolver
from ...task.parse_options import ParseOptions
from ..string_builder import SB
from ..task_printer import TaskPrinter


class TaskManager:
    __instance: TaskManager = None

    def instance() -> TaskManager:
        if TaskManager.__instance is None:
            TaskManager.__instance = TaskManager()
        return TaskManager.__instance

    def __init__(self) -> None:
        self._task_stack: Deque[Task] = Deque()
        self._printer = TaskPrinter()

    def add(self, task: Task):
        self._task_stack.extend(TaskResolver.resolve(task))

    def add_id(self, task_id: Task.ID):
        identity = TaskResolver.find_task(task_id)
        if identity is None:
            raise LookupError(
                SB()
                .append("Task ")
                .append(task_id, SB.Color.CYAN, True)
                .append(" not found")
                .str()
            )
        self.add(identity.creator())

    def print(self, message: str):
        self._printer.write(message)

    def execute(self) -> bool:
        args = Task.Args()
        self._printer.start()
        self._task_stack.append(ParseOptions(self._task_stack))

        while len(self._task_stack) > 0:
            current = self._task_stack.pop()

            describe = current.describe(args)
            if (not describe is None) and len(describe) != 0:
                self._printer.set_task_description(describe)

            try:
                output = current.execute(args)
            except BaseException as error:
                output = Task.Result(args, error, success=False)

            self._printer.set_result(output)

            if not output.success:
                self._printer.stop()
                return False
            args = output.args

        self._printer.stop()
        return True
