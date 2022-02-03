from typing import List, Optional
from .process import Process
from subprocess import run


class _SubProcess(Process):
    def __init__(self, executable: str, arguments: Optional[List[str]] = None) -> None:
        super().__init__(executable, arguments)
        self._executable: str = executable
        self._arguments: List[str] = [] if arguments is None else arguments

    def run(self):
        output = run(
            [self._executable] + self._arguments,
            shell=True,
            capture_output=True,
            text=True,
        )
        self.exit_code = output.returncode
        self.output = (
            ("" if output.stdout is None else output.stdout)
            + "\n"
            + ("" if output.stderr is None else output.stdoerr)
        )
