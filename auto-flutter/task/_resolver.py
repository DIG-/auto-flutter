from collections import deque
from queue import Queue
from typing import Deque, Optional
from ..core.task import Task, TaskIdentity


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

    def find_task(id: str) -> Optional[TaskIdentity]:
        from ..core.task import task_list, user_task

        if id in task_list:
            return task_list[id]
        if id in user_task:
            return user_task[id]
        return None
