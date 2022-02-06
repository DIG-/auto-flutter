from ...core.process import Process
from ...model.config import Config
from ...model.task import Task
from ..flutter import FLUTTER_DISABLE_VERSION_CHECK


class SetupCheckFlutter(Task):
    def __init__(
        self,
        skip_on_failure: bool = False,
    ) -> None:
        super().__init__()
        self._skip = skip_on_failure

    def describe(self, args: Task.Args) -> str:
        return "Checking fluter"

    def execute(self, args: Task.Args) -> Task.Result:
        process = Process.create(
            Config.instance().flutter, [FLUTTER_DISABLE_VERSION_CHECK, "--version"]
        )
        output = process.try_run()
        if isinstance(output, BaseException):
            return Task.Result(args, error=output, success=self._skip)
        if output == False:
            return Task.Result(
                args,
                error=RuntimeError(
                    "Flutter command return with code #" + str(process.exit_code)
                ),
                success=self._skip,
            )
        return Task.Result(args)
