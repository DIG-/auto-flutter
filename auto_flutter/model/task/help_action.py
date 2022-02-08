from __future__ import annotations

from abc import ABC, abstractmethod
from argparse import Action
from operator import itemgetter
from typing import Callable, List, Optional, Tuple, TypeVar

from ...core.utils import _Iterable
from .task import Task


class HelpAction(ABC):
    T = TypeVar("T")

    class Action(Tuple[str, List[Task.Option]]):
        def __new__(
            cls: type[Action], action: str, options: List[Task.Option]
        ) -> Action:
            return super().__new__(Action, (action, options))

        action: str = property(itemgetter(0))
        options: List[Task.Option] = property(itemgetter(1))

    @staticmethod
    def _resolve_options_for_task(task: Task) -> List[Task.Option]:
        from ...core.task.resolver import TaskResolver

        return _Iterable.flatten(
            map(lambda task: task.identity.options, TaskResolver.resolve(task))
        )

    @classmethod
    def _get_action(self, args: Task.Args, decoder: Callable[[str], T]) -> Optional[T]:
        action = args.get_value("-1")
        if action is None:
            return None
        return decoder(action)

    @classmethod
    @abstractmethod
    def actions(self) -> List[Action]:
        raise NotImplementedError()
