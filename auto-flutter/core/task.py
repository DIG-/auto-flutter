from __future__ import annotations
from abc import ABCMeta, abstractclassmethod
from typing import List, Optional
from arguments import Args


class Task(metaclass=ABCMeta):
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def require(self) -> List[Task]:
        return []

    @abstractclassmethod
    def execute(self, args: Args) -> Optional[Args]:
        # Return None when fail
        # Otherwise return given Args with extra args
        raise NotImplementedError
