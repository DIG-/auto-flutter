from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from .task import TaskIdentity


class HelpAction(ABC):
    @abstractmethod
    def actions(self) -> List[TaskIdentity]:
        raise NotImplementedError()
