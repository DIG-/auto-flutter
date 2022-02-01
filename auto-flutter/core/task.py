from __future__ import annotations
from abc import ABCMeta, abstractclassmethod
from lib2to3.pytree import Base
from operator import itemgetter
from typing import Any, Callable, List, Optional, Tuple
from ..core.arguments import Args, Option
from ..model.task_id import TaskId


class TaskIdentity(Tuple[TaskId, str, List[Option], Callable[[], Any]]):
    def __new__(
        cls: type[TaskIdentity],
        id: TaskId,
        name: str,
        options: List[Option],
        creator: Callable[[], Task],
    ) -> TaskIdentity:
        return super().__new__(TaskIdentity, (id, name, options, creator))

    id: TaskId = property(itemgetter(0))
    name: str = property(itemgetter(1))
    options: List[Option] = property(itemgetter(2))
    creator: Callable[[], Task] = property(itemgetter(3))

    def to_map(self) -> Tuple[TaskId, TaskIdentity]:
        return (self.id, self)


class TaskResult:
    args: Args
    error: Optional[BaseException]
    success: bool

    def __init__(
        self, args: Args, error: Optional[BaseException] = None, success: bool = True
    ) -> None:
        self.args = args
        self.error = error
        self.success = success


class Task(metaclass=ABCMeta):
    identity: TaskIdentity = None

    def require(self) -> List[TaskId]:
        return []

    def describe(self, args: Args) -> str:
        return self.identity.name

    @abstractclassmethod
    def execute(self, args: Args) -> TaskResult:
        # Return None when fail
        # Otherwise return given Args with extra args
        raise NotImplementedError
