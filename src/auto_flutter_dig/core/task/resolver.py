from __future__ import annotations

from abc import ABC
from collections import deque
from typing import Deque, Iterable, List, Optional, Union

from ...model.error import TaskNotFound
from ...model.task import *
from ...model.task.subtask import Subtask
from ._unique_identity import _TaskUniqueIdentity


class TaskResolver(ABC):
    @staticmethod
    def resolve(
        task: Union[Task, Iterable[Task], TaskIdentity, Iterable[TaskIdentity]],
        previous: List[TaskIdentity] = [],
        origin: Optional[Subtask] = None,
    ) -> Deque[TaskIdentity]:
        temp: List[TaskIdentity] = []
        if isinstance(task, Task):
            temp = [_TaskUniqueIdentity(task)]
        elif isinstance(task, TaskIdentity):
            temp = [task]
        elif isinstance(task, Iterable):
            for it in task:
                if isinstance(it, Task):
                    temp.append(_TaskUniqueIdentity(it))
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
        temp = TaskResolver.__resolve_dependencies(temp, origin)
        temp.reverse()
        temp = TaskResolver.__clear_repeatable(temp, previous)
        output: Deque[TaskIdentity] = deque()
        for identity in temp:
            output.appendleft(identity)
        return output

    @staticmethod
    def __resolve_dependencies(
        items: List[TaskIdentity],
        origin: Optional[Subtask] = None,
    ) -> List[TaskIdentity]:
        if len(items) <= 0:
            raise IndexError("Require at least one TaskIdentity")
        i = 0
        while i < len(items):
            current = items[i]
            _task: Task = current.creator()
            for id in _task.require():
                identity = TaskResolver.find_task(id, origin)
                if identity is None:
                    raise TaskNotFound(id)
                j = i + 1
                items[j:j] = [identity]
            i += 1
        return items

    @staticmethod
    def __clear_repeatable(
        new: List[TaskIdentity], previous: List[TaskIdentity] = []
    ) -> List[TaskIdentity]:
        items = previous.copy()
        items.extend(new)
        start = len(previous)
        i = start
        while i < len(items):
            n_item = items[i]
            if n_item.allow_more:
                pass
            else:
                j = i - 1
                while j >= 0:
                    p_item = items[j]
                    if p_item.id == n_item.id:
                        del items[i]
                        i -= 1
                        break
                    j -= 1
            i += 1
        return items[start:]

    @staticmethod
    def find_task(
        id: TaskId, origin: Optional[Subtask] = None
    ) -> Optional[TaskIdentity]:
        if origin is None:
            from ...aflutter.task.root import Root

            origin = Root
        if id in origin.subtasks:
            return origin.subtasks[id]
        if not origin.parent is None:
            # Recursive, not good, but not expexct to have more than 3 level
            return TaskResolver.find_task(id, origin.parent)
        return None
