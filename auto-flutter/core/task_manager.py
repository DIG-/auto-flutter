from collections import deque
from typing import Deque
from ..core.task import Task
from ..core.arguments import Args
from ..task.parse_options import ParseOptions


class TaskManager:
    _task_stack: Deque[Task] = deque()

    def add(self, task: Task, depth: int = 0):
        if depth >= 1000:
            raise RecursionError("Task require too much tasks")

        self._task_stack.append(task)
        for subtask in reversed(task.require()):
            self.add(subtask, depth + 1)

    def execute(self) -> bool:
        args = Args()
        self._task_stack.append(ParseOptions(self._task_stack))
        while len(self._task_stack) > 0:
            current = self._task_stack.pop()
            print(current.describe(args))
            output = current.execute(args)
            if output is None:
                print("Task failed")
                return False
            args = output
        print("Finish successfully")
        return True
