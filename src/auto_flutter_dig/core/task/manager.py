from __future__ import annotations

from typing import Deque, Iterable, Union

from ...core.utils import _Ensure
from ...model.error import TaskNotFound
from ...model.task import *
from .printer import TaskPrinter
from .resolver import TaskResolver

__all__ = ["TaskManager"]


class __TaskManager:
    def __init__(self) -> None:
        self._task_stack: Deque[TaskIdentity] = Deque()
        self._task_done: List[TaskIdentity] = []
        self._printer = TaskPrinter()

    def add(
        self, tasks: Union[Task, Iterable[Task], TaskIdentity, Iterable[TaskIdentity]]
    ):
        if (
            not isinstance(tasks, Task)
            and not isinstance(tasks, TaskIdentity)
            and not isinstance(tasks, Iterable)
        ):
            raise TypeError(
                "Field `tasks` must be instance of `Task` or `TaskIdentity` or `Iterable` of both, but `{}` was received".format(
                    type(tasks)
                )
            )
        self._task_stack.extend(TaskResolver.resolve(tasks, self._task_done))

    def add_id(self, ids: Union[TaskId, Iterable[TaskId]]):
        if isinstance(ids, TaskId):
            self.add(self.__find_task(ids))
        elif isinstance(ids, Iterable):
            self.add(map(lambda id: self.__find_task(id), ids))
        else:
            raise TypeError(
                "Field `ids` must be instance of `TaskId` or `Iterable[TaskId]`, but `{}` was received".format(
                    type(ids)
                )
            )

    def start_printer(self):
        self._printer.start()

    def stop_printer(self):
        self._printer.stop()

    def __find_task(self, id: TaskId) -> TaskIdentity:
        _Ensure.type(id, TaskId, "id")
        identity = TaskResolver.find_task(id)
        if identity is None:
            raise TaskNotFound(id)
        return identity

    def print(self, message: str):
        _Ensure.type(message, str, "message")
        self._printer.write(message)

    def execute(self) -> bool:
        args = Args()

        while len(self._task_stack) > 0:
            identity = self._task_stack.pop()
            task = identity.creator()

            describe = task.describe(args)
            if (not describe is None) and len(describe) != 0:
                self._printer.set_task_description(describe)

            try:
                output = task.execute(args)
            except BaseException as error:
                output = TaskResult(args, error, success=False)
            if not isinstance(output, TaskResult):
                output = TaskResult(
                    args,
                    AssertionError(
                        "Task {} returned without result".format(type(task).__name__)
                    ),
                    success=False,
                )

            self._task_done.append(identity)
            self._printer.set_result(output)

            if not output.success:
                return False
            args = output.args

        return True


TaskManager = __TaskManager()
