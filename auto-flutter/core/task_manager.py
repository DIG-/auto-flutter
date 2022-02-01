from typing import Deque
from ..core.logger import log
from ..core.task import Task
from ..core.arguments import Args
from ..task._list import task_list
from ..task._resolver import TaskResolver
from ..task.help import Help
from ..task.parse_options import ParseOptions


class TaskManager:
    _task_stack: Deque[Task]

    def add(self, task: Task):
        if type(task) is Help:
            task = Help(task_list)
        self._task_stack = TaskResolver.resolve(task)

    def execute(self) -> bool:
        args = Args()
        self._task_stack.append(ParseOptions(self._task_stack))
        while len(self._task_stack) > 0:
            current = self._task_stack.pop()
            describe = current.describe(args)
            if (not describe is None) and len(describe) != 0:
                print(describe)
            output = current.execute(args)
            if not output.error is None:
                log.error(str(output.error))
            if not output.success:
                print("Task failed")
                return False
            args = output.args
        print("Finish successfully")
        return True
