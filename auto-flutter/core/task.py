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


class TaskResult(Tuple[Args, Optional[BaseException], bool]):
    def __new__(
        cls: type[TaskResult],
        args: Args,
        error: Optional[BaseException] = None,
        success: bool = True,
    ) -> TaskResult:
        return super().__new__(TaskResult, (args, error, success))

    args: Args = property(itemgetter(0))
    error: Optional[BaseException] = property(itemgetter(1))
    success: bool = property(itemgetter(2))


class Task(metaclass=ABCMeta):
    ## Start - Alias to reduce import
    ID = TaskId
    Args = Args
    Result = TaskResult
    Identity = TaskIdentity
    ## End - alias

    identity: Identity = None

    def require(self) -> List[Task.ID]:
        return []

    def describe(self, args: Task.Args) -> str:
        return self.identity.name

    @abstractclassmethod
    def execute(self, args: Task.Args) -> Task.Result:
        # Return None when fail
        # Otherwise return given Args with extra args
        raise NotImplementedError
