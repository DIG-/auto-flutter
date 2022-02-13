from __future__ import annotations

from typing import Deque, Iterable, Union

from ...core.utils import _Ensure
from ...model.error import TaskNotFound
from ...model.task import Task
from ..string import SB
from .printer import TaskPrinter
from .resolver import TaskResolver

__all__ = ["TaskManager"]


class __TaskManager:
    def __init__(self) -> None:
        self._task_stack: Deque[Task] = Deque()
        self._printer = TaskPrinter()

    def add(
        self, tasks: Union[Task, Iterable[Task], Task.Identity, Iterable[Task.Identity]]
    ):
        if (
            not isinstance(tasks, Task)
            and not isinstance(tasks, Task.Identity)
            and not isinstance(tasks, Iterable)
        ):
            raise TypeError(
                "Field `tasks` must be instance of `Task` or `Task.Identity` or `Iterable` of both, but `{}` was received".format(
                    type(tasks)
                )
            )

        self._task_stack.extend(TaskResolver.resolve(tasks))

    def add_id(self, ids: Union[Task.ID, Iterable[Task.ID]]):
        if isinstance(ids, Task.ID):
            self.add(self.__find_task(ids))
        elif isinstance(ids, Iterable):
            self.add(map(lambda id: self.__find_task(id), ids))
        else:
            raise TypeError(
                "Field `ids` must be instance of `Task.ID` or `Iterable[Task.ID]`, but `{}` was received".format(
                    type(ids)
                )
            )

    def __find_task(self, id: Task.ID) -> Task.Identity:
        _Ensure.type(id, Task.ID, "id")
        identity = TaskResolver.find_task(id)
        if identity is None:
            raise TaskNotFound(id)
        return identity

    def print(self, message: str):
        _Ensure.type(message, str, "message")
        self._printer.write(message)

    def execute(self) -> bool:
        args = Task.Args()
        self._printer.start()

        while len(self._task_stack) > 0:
            current = self._task_stack.pop()

            describe = current.describe(args)
            if (not describe is None) and len(describe) != 0:
                self._printer.set_task_description(describe)

            try:
                output = current.execute(args)
            except BaseException as error:
                output = Task.Result(args, error, success=False)
            if not isinstance(output, Task.Result):
                output = Task.Result(
                    args,
                    AssertionError(
                        "Task {} returned without result".format(type(current).__name__)
                    ),
                    success=False,
                )

            self._printer.set_result(output)

            if not output.success:
                self._printer.stop()
                return False
            args = output.args

        self._printer.stop()
        return True


TaskManager = __TaskManager()
