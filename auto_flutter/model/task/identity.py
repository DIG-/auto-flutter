from __future__ import annotations

from typing import Callable, List, Tuple

from ...core.utils import _Ensure
from ..argument import Option
from .id import TaskId


class TaskIdentity:
    def __init__(
        self,
        id: TaskId,
        name: str,
        options: List[Option],
        creator: Callable[[], "Task"],
        allow_more: bool = False,  # Allow more tasks with same id
    ) -> None:
        from .task import Task

        self.id: TaskId = _Ensure.instance(id, TaskId, "id")
        self.name: str = _Ensure.instance(name, str, "name")
        self.options: List[Option] = _Ensure.instance(options, List, "options")
        self.creator: Callable[[], Task] = _Ensure.instance(
            creator, Callable, "creator"
        )
        self.allow_more: bool = _Ensure.instance(allow_more, bool, "allow_more")

    def to_map(self) -> Tuple[TaskId, TaskIdentity]:
        return (self.id, self)
