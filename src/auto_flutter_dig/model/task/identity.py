from __future__ import annotations

from typing import Callable, List, Tuple

from ...core.utils import _Ensure, _EnsureCallable
from ..argument.option import Option
from .id import TaskId

__all__ = ["TaskIdentity", "TaskId", "List", "Callable", "Option"]


class TaskIdentity:
    def __init__(
        self,
        group: str,
        id: TaskId,
        name: str,
        options: List[Option],
        creator: Callable[[], "Task"],  # type: ignore[name-defined]
        allow_more: bool = False,  # Allow more tasks with same id
    ) -> None:
        from .task import Task

        self.group: str = _Ensure.instance(group, str, "group")
        self.id: TaskId = _Ensure.instance(id, TaskId, "id")
        self.name: str = _Ensure.instance(name, str, "name")
        if not isinstance(options, List):
            _Ensure._raise_error_instance("options", List, type(options))
        self.options: List[Option] = _Ensure.not_none(options, "options")
        self.creator: Callable[[], Task] = _EnsureCallable.instance(creator, "creator")
        self.allow_more: bool = _Ensure.instance(allow_more, bool, "allow_more")

    def to_map(self) -> Tuple[TaskId, TaskIdentity]:
        return (self.id, self)

    def __repr__(self) -> str:
        return "{cls}(group={group}, id={id}, name={name}, options={options}, creator={creator}, allow_more={allow_more})".format(
            cls=type(self).__name__,
            group=self.group,
            id=self.id,
            name=self.name,
            options=self.options,
            creator=self.creator,
            allow_more=self.allow_more,
        )
