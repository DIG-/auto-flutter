from __future__ import annotations

from typing import Deque, Iterable, Optional, Union

from ...core.utils import _Ensure
from ...model.error import TaskNotFound
from ...model.result import Result
from ...model.task import *
from ...model.task.result import TaskResultHelp
from ...model.task.group import TaskGroup
from .printer import *
from .resolver import TaskResolver

__all__ = ["TaskManager"]


class __TaskManager:
    def __init__(self) -> None:
        self._task_stack: Deque[TaskIdentity] = Deque()
        self._task_done: List[TaskIdentity] = []
        self._printer = TaskPrinter()

    def add(
        self,
        tasks: Union[Task, Iterable[Task], TaskIdentity, Iterable[TaskIdentity]],
    ):
        if not isinstance(tasks, Task) and not isinstance(tasks, TaskIdentity) and not isinstance(tasks, Iterable):
            raise TypeError(
                "Field `tasks` must be instance of `Task` or `TaskIdentity` or `Iterable` of both, but `{}` was received".format(
                    type(tasks).__name__
                )
            )
        self._task_stack.extend(TaskResolver.resolve(tasks, self._task_done))

    def add_id(
        self,
        ids: Union[TaskId, Iterable[TaskId]],
        origin: Optional[TaskGroup] = None,
    ):
        if isinstance(ids, TaskId):
            self.add(self.__find_task(ids, origin))
        elif isinstance(ids, Iterable):
            self.add(map(lambda id: self.__find_task(id, origin), ids))
        else:
            raise TypeError(
                "Field `ids` must be instance of `TaskId` or `Iterable[TaskId]`, but `{}` was received".format(
                    type(ids).__name__
                )
            )

    def start_printer(self):
        self._printer.start()

    def stop_printer(self):
        self._printer.stop()

    def __find_task(
        self,
        id: TaskId,
        origin: Optional[TaskGroup] = None,
    ) -> TaskIdentity:
        _Ensure.type(id, TaskId, "id")
        return TaskResolver.find_task(id, origin)

    def print(self, message: str):
        self._printer.append(OpMessage(message))

    def update_description(
        self,
        description: Optional[str],
        result: Optional[Result] = None,
    ):
        if not result is None:
            self._printer.append(OpResult(result))
        self._printer.append(OpDescription(description))

    def execute(self) -> bool:
        args = Args()
        had_failure = False
        while len(self._task_stack) > 0:
            identity = self._task_stack.pop()
            task = identity.creator()
            args.select_group(identity.group)
            task.log.info("Starting task")

            self._printer.append(OpDescription(task.describe(args)))

            try:
                output = task.execute(args)
            except BaseException as error:
                output = TaskResult(args, error, success=False)
            if not isinstance(output, TaskResult):
                output = TaskResult(
                    args,
                    AssertionError("Task {} returned without result".format(type(task).__name__)),
                    success=False,
                )

            self._task_done.append(identity)
            self._printer.append(OpResult(output))

            if not output.message is None:
                task.log.debug(output.message)
            if output.is_success:
                task.log.info("Finished successfully")
            elif output.is_warning:
                task.log.warning("Finished with warning", exc_info=output.error)
            elif output.is_error:
                task.log.error("Failed", exc_info=output.error)

            if not output.success:
                if isinstance(output, TaskResultHelp):
                    from ...module.aflutter.task.help import HelpTask

                    self._task_stack.clear()
                    self.add(HelpTask.Stub(identity))
                    had_failure = True
                    continue
                return False
            args = output.args

        return not had_failure

    def __repr__(self) -> str:
        return "TaskManager(stack_size={stack_size}, done_size={done_size}, stack={stack}, done={done})".format(
            stack_size=len(self._task_stack),
            done_size=len(self._task_done),
            stack=self._task_stack,
            done=self._task_done,
        )


TaskManager = __TaskManager()
