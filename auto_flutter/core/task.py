from __future__ import annotations
from abc import ABCMeta, abstractclassmethod
from operator import itemgetter
from typing import Any, Callable, List, Optional, Tuple
from ..core.arguments import Args, Option
from ..core.utils import _Ensure
from ..model.task_id import TaskId


class TaskIdentity(Tuple[TaskId, str, List[Option], Callable[[], Any]]):
    ## Start - Alias to reduce import
    Option = Option
    ## End - Alias
    def __new__(
        cls: type[TaskIdentity],
        id: TaskId,
        name: str,
        options: List[Option],
        creator: Callable[[], Task],
    ) -> TaskIdentity:
        _Ensure.type(id, TaskId, "id")
        _Ensure.type(name, str, "name")
        _Ensure.type(options, List, "options")
        _Ensure.type(creator, Callable, "creator")
        return super().__new__(TaskIdentity, (id, name, options, creator))

    id: TaskId = property(itemgetter(0))
    name: str = property(itemgetter(1))
    options: List[Option] = property(itemgetter(2))
    creator: Callable[[], Task] = property(itemgetter(3))

    def to_map(self) -> Tuple[TaskId, TaskIdentity]:
        return (self.id, self)


class TaskResult(Tuple[Args, Optional[BaseException], Optional[str], bool]):
    def __new__(
        cls: type[TaskResult],
        args: Args,
        error: Optional[BaseException] = None,
        message: Optional[str] = None,
        success: Optional[bool] = None,
    ) -> TaskResult:
        _Ensure.type(args, Args, "args")
        _Ensure.type(error, BaseException, "error")
        _Ensure.type(message, str, "message")
        _Ensure.type(success, bool, "success")
        if success is None:
            if error is None:
                success = True
            else:
                success = False
        return super().__new__(TaskResult, (args, error, message, success))

    args: Args = property(itemgetter(0))
    error: Optional[BaseException] = property(itemgetter(1))
    message: Optional[str] = property(itemgetter(2))
    success: bool = property(itemgetter(3))


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

    def print(self, message: str):
        from ..core.task_manager import TaskManager

        TaskManager.instance().print(message)

    @abstractclassmethod
    def execute(self, args: Task.Args) -> Task.Result:
        # Return None when fail
        # Otherwise return given Args with extra args
        raise NotImplementedError
