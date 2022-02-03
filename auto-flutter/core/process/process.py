from __future__ import annotations
from abc import ABCMeta, abstractmethod
from pathlib import PurePath
from typing import Callable, List, Optional, Union
from ..os import OS
from ..utils import _Ensure


class Process(metaclass=ABCMeta):
    def create(
        executable: Union[str, PurePath],
        arguments: Optional[List[str]] = None,
        writer: Optional[Callable[[str], None]] = None,
    ) -> Process:
        from .subprocess import _SubProcess

        return _SubProcess(executable, arguments, writer)

    def __init__(
        self,
        executable: Union[str, PurePath],
        arguments: Optional[List[str]] = None,
        writer: Optional[Callable[[str], None]] = None,
    ) -> None:
        _Ensure.type(executable, (str, PurePath), "executable")
        self.output: Optional[str] = None
        self.exit_code: int = -1
        self._executable: PurePath = OS.posix_to_machine_path(
            _Ensure.not_none(executable, "executable")
        )
        self._arguments = [] if arguments is None else arguments
        self._writer = writer
        self.__writer_buffer: str = ""

    def _write_output(self, message: str):
        if self._writer is None:
            return
        self.__writer_buffer += message
        index = self.__writer_buffer.rfind("\n")
        if index != -1:
            self._writer(self.__writer_buffer[:index])
            if index + 1 >= len(self.__writer_buffer):
                self.__writer_buffer = ""
            else:
                self.__writer_buffer = self.__writer_buffer[index + 1]

    @abstractmethod
    def run(self):
        raise NotImplementedError("This method must be implemented")
