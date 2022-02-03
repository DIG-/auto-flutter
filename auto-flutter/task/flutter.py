from aifc import Error
from pprint import pprint
from typing import List, Optional, Tuple
from ..core.task import Task
from ..core.process.process import Process
from ..task.project_read import ProjectRead
from ..model.config import Config


class Flutter(Task):
    identity = Task.Identity("exec", "Run flutter command", [], lambda: Flutter())

    class Error(ChildProcessError):
        ...

    def __init__(
        self,
        project: bool = True,
        command: Optional[List[str]] = None,
        output: bool = False,
    ) -> None:
        super().__init__()
        self._project: bool = project
        self._command: Optional[List[str]] = command
        self._output: bool = output

    def require(self) -> List[Task.ID]:
        if self._project:
            return [ProjectRead.identity.id]
        return [ProjectRead.identity_skip.id]

    def execute(self, args: Task.Args) -> Task.Result:
        flutter = Config.instance().flutter
        if not self._command is None and len(self._command) > 0:
            p = Process.create(flutter, self._command, lambda x: self.print(x))
            p.run()
            if self._output:
                return Task.Result(
                    args,
                    error=Flutter.Error(p.exit_code, p.output),
                    success=p.exit_code == 0,
                )
            else:
                return Task.Result(
                    args,
                    success=p.exit_code == 0,
                )

        return Task.Result(error=NotImplementedError("Not yet"))


FlutterDoctor = Task.Identity(
    "doctor", "Run flutter doctor", [], lambda: Flutter(False, ["doctor"])
)
