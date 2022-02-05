from __future__ import annotations

from operator import itemgetter
from typing import Callable, List, Tuple

from ...core.utils import _Ensure
from ..argument import Option
from . import TaskId


class TaskIdentity(Tuple[TaskId, str, List[Option], Callable[[], "Task"]]):
    ## Start - Alias to reduce import
    Option = Option
    ## End - Alias
    def __new__(
        cls: type[TaskIdentity],
        id: TaskId,
        name: str,
        options: List[Option],
        creator: Callable[[], "Task"],
    ) -> TaskIdentity:
        _Ensure.type(id, TaskId, "id")
        _Ensure.type(name, str, "name")
        _Ensure.type(options, List, "options")
        _Ensure.type(creator, Callable, "creator")
        return super().__new__(
            TaskIdentity,
            (
                _Ensure.not_none(id, "id"),
                _Ensure.not_none(name, "name"),
                _Ensure.not_none(options, "options"),
                _Ensure.not_none(creator, "creator"),
            ),
        )

    id: TaskId = property(itemgetter(0))
    name: str = property(itemgetter(1))
    options: List[Option] = property(itemgetter(2))
    creator: Callable[[], "Task"] = property(itemgetter(3))

    def to_map(self) -> Tuple[TaskId, TaskIdentity]:
        return (self.id, self)
