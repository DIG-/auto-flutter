from __future__ import annotations

from typing import Callable, List, Optional, Tuple

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
        from .group import TaskGroup  # pylint: disable=import-outside-toplevel
        from .task import Task  # pylint: disable=import-outside-toplevel

        self.group: str = _Ensure.instance(group, str, "group")
        self.id: TaskId = _Ensure.instance(id, TaskId, "id")
        self.name: str = _Ensure.instance(name, str, "name")
        if not isinstance(options, List):
            _Ensure._raise_error_instance("options", List, type(options))
        self.options: List[Option] = _Ensure.not_none(options, "options")
        self.creator: Callable[[], Task] = _EnsureCallable.instance(creator, "creator")
        self.allow_more: bool = _Ensure.instance(allow_more, bool, "allow_more")
        self.parent: Optional[TaskGroup] = None

    def to_map(self) -> Tuple[TaskId, TaskIdentity]:
        return (self.id, self)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(id={self.id}, group={self.group}, "
            + f"name={self.name}, options={self.options}, creator={self.creator}, "
            + f"parent={self.parent}, allow_more={self.allow_more})"
        )
