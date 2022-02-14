from __future__ import annotations

from abc import ABC
from collections import deque
from typing import Deque, Iterable, List, Optional, Union

from ...model.error import TaskNotFound
from ...model.task import *


class TaskResolver(ABC):
    @staticmethod
    def resolve(
        task: Union[Task, Iterable[Task], TaskIdentity, Iterable[TaskIdentity]]
    ) -> Deque[Task]:
        temp: List[TaskIdentity] = []
        if isinstance(task, Task):
            temp = [TaskResolver.__TaskIdentityWrapper(task)]
        elif isinstance(task, TaskIdentity):
            temp = [task]
        elif isinstance(task, Iterable):
            for it in task:
                if isinstance(it, Task):
                    temp.append(TaskResolver.__TaskIdentityWrapper(it))
                elif isinstance(it, TaskIdentity):
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

    @staticmethod
    def __resolve_dependencies(items: List[TaskIdentity]) -> List[TaskIdentity]:
        if len(items) <= 0:
            raise IndexError("Require at least one TaskIdentity")
        i = 0
        while i < len(items):
            current = items[i]
            _task: Task = current.creator()
            for id in _task.require():
                identity = TaskResolver.find_task(id)
                if identity is None:
                    raise TaskNotFound(id)
                j = i + 1
                items[j:j] = [identity]
            i += 1
        return items

    @staticmethod
    def __clear_repeatable(items: List[TaskIdentity]) -> List[TaskIdentity]:
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

    @staticmethod
    def find_task(id: TaskId) -> Optional[TaskIdentity]:
        from ...task._list import task_list, user_task

        if id in task_list:
            return task_list[id]
        if id in user_task:
            return user_task[id]
        return None

    class __TaskIdentityWrapper:
        def __new__(
            cls: type[TaskResolver.__TaskIdentityWrapper], task: Task
        ) -> TaskIdentity:
            return TaskIdentity("-#-#-", "", [], lambda: task, True)
