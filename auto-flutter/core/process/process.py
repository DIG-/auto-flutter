from __future__ import annotations
from abc import ABCMeta, abstractmethod
from os import environ
from pathlib import PurePath
from typing import Callable, Dict, List, Optional, Union
from ..os import OS
from ..utils import _Ensure


class Process(metaclass=ABCMeta):
    def create(
        executable: Union[str, PurePath],
        arguments: Optional[List[str]] = None,
        environment: Optional[Dict[str, str]] = None,
        writer: Optional[Callable[[str], None]] = None,
        inherit_environment: bool = True,
    ) -> Process:
        from .subprocess import _SubProcess

        return _SubProcess(
            executable, arguments, environment, writer, inherit_environment
        )

    def __init__(
        self,
        executable: Union[str, PurePath],
        arguments: Optional[List[str]] = None,
        environment: Optional[Dict[str, str]] = None,
        writer: Optional[Callable[[str], None]] = None,
        inherit_environment: bool = True,
    ) -> None:
        _Ensure.type(executable, (str, PurePath), "executable")
        _Ensure.type(arguments, List, "arguments")
        _Ensure.type(environment, Dict, "environment")
        _Ensure.type(writer, Callable, "writer")
        _Ensure.type(inherit_environment, bool, "inherit_environment")
        self.output: Optional[str] = None
        self.exit_code: int = -1
        self._executable: PurePath = OS.posix_to_machine_path(
            _Ensure.not_none(executable, "executable")
        )
        environment = {} if environment is None else environment
        if inherit_environment:
            current_env = environ.copy()
            self._environment = {**current_env, **environment}
        else:
            self._environment = environment
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

    def try_run(self) -> Union[bool, BaseException]:
        try:
            self.run()
        except BaseException as error:
            return error
        return self.exit_code == 0

    @abstractmethod
    def run(self):
        raise NotImplementedError("This method must be implemented")
