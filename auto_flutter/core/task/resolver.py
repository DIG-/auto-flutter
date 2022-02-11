from __future__ import annotations

from collections import deque
from typing import Deque, Iterable, List, Optional, Union

from auto_flutter.model.task.identity import TaskIdentity

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

    def resolve(
        task: Union[Task, Iterable[Task], Task.Identity, Iterable[Task.Identity]]
    ) -> Deque[Task]:
        temp: List[Task.Identity] = []
        if isinstance(task, Task):
            temp = [TaskResolver.__TaskIdentityWrapper(task)]
        elif isinstance(task, TaskIdentity):
            temp = [task]
        elif isinstance(task, Iterable):
            for it in task:
                if isinstance(it, Task):
                    temp.append(TaskResolver.__TaskIdentityWrapper(it))
                elif isinstance(it, Task.Identity):
                    temp.append(it)
                else:
                    raise TypeError(
                        "Trying to resolve task, but received {}".format(type(task))
                    )
        else:
            raise TypeError(
                "Trying to resolve task, but received {}".format(type(task))
            )
        temp = TaskResolver.__resolve_dependencies(temp)
        temp.reverse()
        temp = TaskResolver.__clear_repeatable(temp)
        output: Deque[Task] = deque()
        for identity in temp:
            output.appendleft(identity.creator())
        return output

    def __resolve_dependencies(items: List[Task.Identity]) -> List[Task.Identity]:
        if len(items) <= 0:
            raise IndexError("Require at least one Task.Identity")
        i = 0
        while i < len(items):
            current = items[i]
            _task: Task = current.creator()
            for id in _task.require():
                identity = TaskResolver.find_task(id)
                if identity is None:
                    raise LookupError('Task not found "{}"'.format(id))
                j = i + 1
                items[j:j] = [identity]
            i += 1
        return items

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

    class __TaskIdentityWrapper:
        def __new__(
            cls: type[TaskResolver.__TaskIdentityWrapper], task: Task
        ) -> Task.Identity:
            return Task.Identity("-#-#-", "", [], lambda: task, True)
