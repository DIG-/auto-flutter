from typing import List, Optional
from ..core.task import Task
from ..core.process.process import Process
from ..task.project_read import ProjectRead
from ..model.config import Config
from ..core.arguments import OptionAll


class Flutter(Task):
    identity = Task.Identity(
        "exec", "Run flutter command", [OptionAll()], lambda: Flutter()
    )

    class Error(ChildProcessError):
        ...

    def __init__(
        self,
        project: bool = True,
        command: Optional[List[str]] = None,
        command_append_args: bool = False,
        output: bool = False,
    ) -> None:
        super().__init__()
        self._project: bool = project
        self._command: Optional[List[str]] = command
        self._command_args: bool = command_append_args
        self._output: bool = output

    def require(self) -> List[Task.ID]:
        if self._project:
            return [ProjectRead.identity.id]
        return [ProjectRead.identity_skip.id]

    def execute(self, args: Task.Args) -> Task.Result:
        flutter = Config.instance().flutter
        if not self._command is None and len(self._command) > 0:
            if self._command_args:
                self._command.extend(args.to_command_arg())
            p = Process.create(
                flutter, arguments=self._command, writer=lambda x: self.print(x)
            )
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
        p = Process.create(
            flutter, arguments=args.to_command_arg(), writer=lambda x: self.print(x)
        )
        output = p.try_run()
        if isinstance(output, BaseException):
            return Task.Result(args, error=output)
        return Task.Result(
            args,
            error=Flutter.Error(p.exit_code, p.output) if self._output else None,
            success=output,
        )


FlutterDoctor = Task.Identity(
    "doctor",
    "Run flutter doctor",
    [OptionAll()],
    lambda: Flutter(False, ["doctor"], command_append_args=True),
)
