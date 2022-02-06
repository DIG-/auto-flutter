from ...core.process import Process
from ...model.config import Config
from ...model.task import Task
from ._const import FIREBASE_DISABLE_INTERACTIVE_MODE, FIREBASE_ENV


class FirebaseCheck(Task):
    def __init__(self, skip_on_failure: bool = False) -> None:
        super().__init__()
        self._skip = skip_on_failure

    def describe(self, args: Task.Args) -> str:
        return "Checking firebase-cli"

    def execute(self, args: Task.Args) -> Task.Result:
        process = Process.create(
            Config.instance().firebase,
            arguments=[FIREBASE_DISABLE_INTERACTIVE_MODE, "--version"],
            environment=FIREBASE_ENV,
        )
        output = process.try_run()
        if isinstance(output, BaseException):
            return Task.Result(args, error=output, success=self._skip)
        if output == False:
            return Task.Result(
                args,
                error=RuntimeError(
                    "Firebase-cli command return with code #" + str(process.exit_code)
                ),
                success=self._skip,
            )
        return Task.Result(args)
