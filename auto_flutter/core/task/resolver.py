from collections import deque
from typing import Deque, List, Optional

from ...model.task import Task


class TaskResolver:
    """
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
    """

    def resolve(task: Task) -> Deque[Task]:
        temp = TaskResolver.__resolve_dependencies(task)
        temp.reverse()
        temp = TaskResolver.__clear_repeatable(temp)
        output: Deque[Task] = deque()
        for identity in temp:
            output.appendleft(identity.creator())
        return output

    def __resolve_dependencies(task: Task) -> List[Task.Identity]:
        temp: List[Task.Identity] = [Task.Identity("-#-#-", "", [], lambda: task, True)]
        i = 0
        while i < len(temp):
            current = temp[i]
            _task = current.creator()
            for id in _task.require():
                identity = TaskResolver.find_task(id)
                if identity is None:
                    raise LookupError('Task not found "{}"'.format(id))
                j = i + 1
                temp[j:j] = [identity]
            i += 1
        return temp

    def __clear_repeatable(items: List[Task.Identity]) -> List[Task.Identity]:
        i = 0
        while i < len(items):
            current = items[i]
            j = i + 1
            while j < len(items):
                it = items[j]
                if it.allow_more:
                    pass
                elif it.id == current.id:
                    del items[j]
                    continue
                j += 1
            i += 1
        return items

    def find_task(id: Task.ID) -> Optional[Task.Identity]:
        from ...task._list import task_list, user_task

        if id in task_list:
            return task_list[id]
        if id in user_task:
            return user_task[id]
        return None
