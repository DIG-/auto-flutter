from collections import deque
from queue import Queue
from typing import Deque, Optional
from ..model.task import TaskId
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
                found = TaskResolver.find_task(required)
                if found is None:
                    raise LookupError('Task not found "{}"'.format(required))
                temp.put(found.creator())
        return output

    def find_task(id: TaskId) -> Optional[TaskIdentity]:
        from ._list import task_list, user_task

        if id in task_list:
            return task_list[id]
        if id in user_task:
            return user_task[id]
        return None
