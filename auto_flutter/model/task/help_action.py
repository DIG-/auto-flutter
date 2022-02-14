from __future__ import annotations

from abc import ABC, abstractclassmethod
from typing import List

from .task import Task


class HelpAction(ABC):
    @abstractclassmethod
    def actions(self) -> List[TaskIdentity]:
        raise NotImplementedError()
