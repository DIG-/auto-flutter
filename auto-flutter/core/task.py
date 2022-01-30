from __future__ import annotations
from abc import ABCMeta, abstractclassmethod
from operator import itemgetter
from typing import Any, Callable, List, Optional, Tuple
from core.arguments import Args


class TaskIdentity(Tuple[str, str, Callable[[], Any]]):
    def __new__(
        cls: type[TaskIdentity], id: str, name: str, creator: Callable[[], Task]
    ) -> TaskIdentity:
        return super().__new__(TaskIdentity, (id, name, creator))

    id: str = property(itemgetter(0))
    name: str = property(itemgetter(1))
    creator: Callable[[], Task] = property(itemgetter(2))


class Task(metaclass=ABCMeta):
    identity: TaskIdentity = None

    def require(self) -> List[Task]:
        return []

    @abstractclassmethod
    def execute(self, args: Args) -> Optional[Args]:
        # Return None when fail
        # Otherwise return given Args with extra args
        raise NotImplementedError
