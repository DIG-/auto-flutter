from collections import deque
from queue import Queue
from typing import Deque
from ..core.task import Task


class TaskResolver:
    def resolve(task: Task) -> Deque[Task]:
        output: Deque[Task] = deque()
        temp = Queue()
        temp.put(task)
        while not temp.empty():
            current: Task = temp.get()
            output.append(current)
            for required in reversed(current.require()):
                temp.put(required)
        return output
