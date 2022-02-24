from __future__ import annotations

from abc import ABC
from typing import Dict, Iterable, Optional, Tuple, Union

from ...core.utils import _Ensure, _Iterable
from .id import TaskId
from .identity import TaskIdentity


class Subtask(ABC):
    def __init__(
        self,
        subtasks: Dict[TaskId, TaskIdentity],
        parent: Optional[Subtask] = None,
    ) -> None:
        super().__init__()
        self.subtasks: Dict[TaskId, TaskIdentity] = subtasks
        self.parent: Optional[Subtask] = parent

    def register_subtask(self, task: Union[TaskIdentity, Iterable[TaskIdentity]]):
        if isinstance(task, TaskIdentity):
            self.__register_subtask_tuple([task.to_map()])
        elif isinstance(task, Iterable):
            self.__register_subtask_tuple(
                _Ensure.instance(x, TaskIdentity, "task").to_map() for x in task
            )
        else:
            raise TypeError("Unexpected type received `{}`".format(type(task).__name__))

    def __register_subtask_tuple(self, tasks: Iterable[Tuple[TaskId, TaskIdentity]]):
        self.__insert_sorted(_Iterable.join(self.subtasks.items(), tasks))
        pass

    def __insert_sorted(self, tasks: Iterable[Tuple[TaskId, TaskIdentity]]):
        self.subtasks = dict(sorted(tasks, key=lambda x: x[0]))
