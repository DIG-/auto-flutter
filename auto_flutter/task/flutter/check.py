from ...core.config import Config
from ...core.process import Process
from ...model.task import *
from ._const import FLUTTER_CONFIG_KEY_PATH, FLUTTER_DISABLE_VERSION_CHECK


class FlutterCheck(Task):
    def __init__(
        self,
        skip_on_failure: bool = False,
    ) -> None:
        super().__init__()
        self._skip = skip_on_failure

    def describe(self, args: Args) -> str:
        return "Checking fluter"

    def execute(self, args: Args) -> TaskResult:
        process = Process.create(
            Config.get_path(FLUTTER_CONFIG_KEY_PATH),
            [FLUTTER_DISABLE_VERSION_CHECK, "--version"],
        )
        output = process.try_run()
        if isinstance(output, BaseException):
            return TaskResult(args, error=output, success=self._skip)
        if output == False:
            return TaskResult(
                args,
                error=RuntimeError(
                    "Flutter command return with code #" + str(process.exit_code)
                ),
                success=self._skip,
            )
        return TaskResult(args)
