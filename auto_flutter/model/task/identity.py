from __future__ import annotations

from operator import itemgetter
from typing import Callable, List, Tuple

from ...core.utils import _Ensure
from ..argument import Option
from . import TaskId


class TaskIdentity(Tuple[TaskId, str, List[Option], Callable[[], "Task"], bool]):
    ## Start - Alias to reduce import
    Option = Option
    ## End - Alias
    def __new__(
        cls: type[TaskIdentity],
        id: TaskId,
        name: str,
        options: List[Option],
        creator: Callable[[], "Task"],
        allow_more: bool = False,  # Allow more tasks with same id
    ) -> TaskIdentity:
        return super().__new__(
            TaskIdentity,
            (
                _Ensure.instance(id, TaskId, "id"),
                _Ensure.instance(name, str, "name"),
                _Ensure.instance(options, List, "options"),
                _Ensure.instance(creator, Callable, "creator"),
                _Ensure.instance(allow_more, bool, "allow_more"),
            ),
        )

    id: TaskId = property(itemgetter(0))
    name: str = property(itemgetter(1))
    options: List[Option] = property(itemgetter(2))
    creator: Callable[[], "Task"] = property(itemgetter(3))
    allow_more: bool = property(itemgetter(4))

    def to_map(self) -> Tuple[TaskId, TaskIdentity]:
        return (self.id, self)
