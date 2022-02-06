from ...core.process import Process
from ...model.config import Config
from ...model.task import Task


class SetupCheck(Task):
    def __init__(
        self,
        flutter: bool = False,
        firebase: bool = False,
        skip_on_failure: bool = False,
    ) -> None:
        super().__init__()
        if not flutter and not firebase:
            raise AttributeError("Require check flutter or firebase")
        self._flutter = flutter
        self._firebase = firebase
        self._skip = skip_on_failure

    def describe(self, args: Task.Args) -> str:
        if self._flutter:
            return "Checking fluter"
        elif self._firebase:
            return "Checking firebase"
        return "Unknown checking"

    def execute(self, args: Task.Args) -> Task.Result:
        if self._flutter:
            return self.__test_flutter(args)
        elif self._firebase:
            return self.__test_firebase(args)
        return Task.Result(
            args,
            error=NotImplementedError("Setup check only accept flutter or firebase"),
        )

    def __test_flutter(self, args: Task.Args) -> Task.Result:
        process = Process.create(Config.instance().flutter, ["--version"])
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

    def __test_firebase(self, args: Task.Args) -> Task.Result:
        env = {"FIREPIT_VERSION": "1"} if Config.instance().firebase_standalone else {}
        process = Process.create(
            Config.instance().firebase, ["--version"], environment=env
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
