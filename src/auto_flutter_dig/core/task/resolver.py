from __future__ import annotations

from abc import ABC
from collections import deque
from typing import Deque, Iterable, List, Optional, Union

from ...core.utils import _If
from ...model.error import TaskNotFound
from ...model.task import *
from ...model.task.group import TaskGroup
from ._unique_identity import _TaskUniqueIdentity


class TaskResolver(ABC):
    @staticmethod
    def resolve(
        task: Union[Task, Iterable[Task], TaskIdentity, Iterable[TaskIdentity]],
        previous: List[TaskIdentity] = [],
        origin: Optional[TaskGroup] = None,
    ) -> Deque[TaskIdentity]:
        temp: List[TaskIdentity] = []
        if isinstance(task, Task):
            t_identity = _TaskUniqueIdentity(task)
            if hasattr(task, "identity") and not task.identity is None:
                t_identity.parent = task.identity.parent
            temp = [t_identity]
        elif isinstance(task, TaskIdentity):
            temp = [task]
        elif isinstance(task, Iterable):
            for it in task:
                if isinstance(it, Task):
                    it_identity = _TaskUniqueIdentity(it)
                    if hasattr(it, "identity") and not it.identity is None:
                        it_identity.parent = it.identity.parent
                    temp.append(it_identity)
                elif isinstance(it, TaskIdentity):
                    temp.append(it)
                else:
                    raise TypeError("Trying to resolve task, but received {}".format(type(task)))
        else:
            raise TypeError("Trying to resolve task, but received {}".format(type(task)))
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
        origin: Optional[TaskGroup] = None,
    ) -> List[TaskIdentity]:
        if len(items) <= 0:
            raise IndexError("Require at least one TaskIdentity")
        i = 0
        while i < len(items):
            current = items[i]
            _task: Task = current.creator()
            for id in _task.require():
                identity = TaskResolver.find_task(
                    id,
                    _If.not_none(origin, lambda x: x, lambda: current.parent),
                )
                j = i + 1
                items[j:j] = [identity]
            i += 1
        return items

    @staticmethod
    def __clear_repeatable(new: List[TaskIdentity], previous: List[TaskIdentity] = []) -> List[TaskIdentity]:
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
    def find_task(id: TaskId, origin: Optional[TaskGroup] = None) -> TaskIdentity:
        if origin is None:
            from ...module.aflutter.task.root import Root

            origin = Root
        if id in origin.subtasks:
            return origin.subtasks[id]
        if not origin.parent is None:
            # Recursive, not good, but not expexct to have more than 3 level
            return TaskResolver.find_task(id, origin.parent)
        raise TaskNotFound(id, origin)
