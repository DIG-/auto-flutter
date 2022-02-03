from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import List, Optional
from .subprocess import _SubProcess


class Process(metaclass=ABCMeta):
    def create(executable: str, arguments: Optional[List[str]] = None) -> Process:
        return _SubProcess(executable, arguments)

    def __init__(self, executable: str, arguments: Optional[List[str]] = None) -> None:
        self.output: Optional[str] = None
        self.exit_code: int = -1

    @abstractmethod
    def run(self):
        raise NotImplementedError("This method must be implemented")
