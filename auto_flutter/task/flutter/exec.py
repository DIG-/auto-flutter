from typing import List, Optional

from ...core.process.process import Process
from ...core.string import SB
from ...model.argument import Arg, OptionAll
from ...model.config import Config
from ...model.task import Task
from ..project.read import ProjectRead
from ._const import FLUTTER_DISABLE_VERSION_CHECK


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
        output_running: bool = True,
        output_end: bool = False,
        output_arg: bool = False,
    ) -> None:
        super().__init__()
        self._project: bool = project
        self._command: Optional[List[str]] = command
        self._command_args: bool = command_append_args
        self._output_running: bool = output_running
        self._output_end: bool = output_end
        self._output_arg: bool = output_arg

    def require(self) -> List[Task.ID]:
        if self._project:
            return [ProjectRead.identity.id]
        return [ProjectRead.identity_skip.id]

    def execute(self, args: Task.Args) -> Task.Result:
        flutter = Config.instance().flutter
        writer = None if not self._output_running else lambda x: self.print(x)

        if self._output_end and self._output_running:
            self.print(
                SB()
                .append("[!] Running command will show output twice", SB.Color.YELLOW)
                .str()
            )

        if not self._command is None and len(self._command) > 0:
            if self._command_args:
                self._command.extend(args.to_command_arg())
            p = Process.create(flutter, arguments=self._command, writer=writer)
        else:
            arguments = [FLUTTER_DISABLE_VERSION_CHECK]
            arguments.extend(args.to_command_arg())
            p = Process.create(flutter, arguments=arguments, writer=writer)
        output = p.try_run()

        if self._output_end:
            self.print(p.output)

        if self._output_arg:
            args["output"] = Arg("output", p.output)

        if isinstance(output, BaseException):
            return Task.Result(args, error=output)
        return Task.Result(
            args,
            success=output,
        )
