from abc import abstractmethod
from pathlib import Path, PurePath, PurePosixPath
from typing import Dict, Iterable, Optional, Union

from ....core.os import OS
from ....core.process import Process
from ....core.string import SF
from ....model.task import *

__all__ = [
    "Task",
    "List",
    "TaskIdentity",
    "TaskResult",
    "TaskId",
    "Option",
    "Args",
    "Process",
    "BaseProcessTask",
]


class BaseProcessTask(Task):
    def __init__(self, ignore_failure: bool = False) -> None:
        super().__init__()
        self._process: Process
        self._ignore_failure: bool = ignore_failure

    def execute(self, args: Args) -> TaskResult:
        self._process = self._create_process(args)
        output = self._process.try_run()
        return self._handle_process_output(args, self._process, output)

    def _sanitize_arguments(
        self,
        arguments: Iterable[str],
        args: Args,
        extras: Optional[Dict[str, str]] = None,
        expand_args: bool = True,
        expand_path: bool = False,
    ) -> List[str]:
        output: List[str] = []
        for argument in arguments:
            if expand_args:
                argument = SF.format(argument, args, extras)
            if argument.startswith("./"):
                path: PurePath = PurePosixPath(argument)
                path = OS.posix_to_machine_path(path)
                if expand_path:
                    path = Path(path).absolute()
                argument = str(path)
            output.append(argument)
        return output

    def _sanitize_executable(self, executable: Union[str, PurePath]) -> PurePath:
        if isinstance(executable, str):
            executable = PurePosixPath(executable)
        if not isinstance(executable, PurePath):
            raise ValueError(
                "executable must be `str` or `PurePath`, but received `{}`".format(
                    type(executable).__name__
                )
            )
        return OS.posix_to_machine_path(executable)

    @abstractmethod
    def _create_process(self, args: Args) -> Process:
        ## Use self._sanitize_executable() before passing to Process
        ## Use self._sanitize_arguments() before passing to Process
        raise NotImplementedError(
            "{} requires to implement _create_process".format(type(self).__name__)
        )

    def _handle_process_output(
        self, args: Args, process: Process, output: Union[bool, BaseException]
    ) -> TaskResult:
        if isinstance(output, bool):
            return self._handle_process_finished(args, process, output)
        elif isinstance(output, BaseException):
            return self._handle_process_exception(args, process, output)
        raise ValueError(
            "Expected `bool` or `BaseException`, but process returned `{}`".format(
                type(output).__name__
            )
        )

    def _handle_process_finished(
        self, args: Args, process: Process, output: bool
    ) -> TaskResult:
        if output and not process.output is None and len(process.output) > 0:
            return TaskResult(args, message=process.output, success=output)
        return TaskResult(args, success=self._ignore_failure or output)

    def _handle_process_exception(
        self, args: Args, process: Process, output: BaseException
    ) -> TaskResult:
        return TaskResult(args, error=output, success=self._ignore_failure)
