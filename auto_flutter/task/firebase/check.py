from threading import Thread
from typing import Optional, Union

from ...core.process import Process
from ...core.string import SB
from ...model.config import Config
from ...model.task import Task
from ._const import FIREBASE_DISABLE_INTERACTIVE_MODE, FIREBASE_ENV


class FirebaseCheck(Task):
    identity = Task.Identity(
        "-firebase-check", "Checking firebase-cli", [], lambda: FirebaseCheck()
    )

    def __init__(self, skip_on_failure: bool = False) -> None:
        super().__init__()
        self._skip = skip_on_failure
        self.__thread = Thread(target=FirebaseCheck.__run, args=[self])
        self.__process: Optional[Process] = None
        self.__output: Union[None, bool, BaseException] = None

    def execute(self, args: Task.Args) -> Task.Result:
        self.__process = Process.create(
            Config.instance().firebase,
            arguments=[FIREBASE_DISABLE_INTERACTIVE_MODE.value, "--version"],
            environment=FIREBASE_ENV.value,
        )
        self.__thread.start()
        process_killed: bool = False
        if self.__thread.is_alive():
            self.__thread.join(5)
        if self.__thread.is_alive():
            self.print("  Still waiting...")
            self.__thread.join(10)
        if self.__thread.is_alive():
            self.print(
                SB().append("  It is taking some time...", SB.Color.YELLOW).str()
            )
            self.__thread.join(15)
        if self.__thread.is_alive():
            self.print(
                SB()
                .append("  Looks like it stuck...\n", SB.Color.RED)
                .append(
                    "  Check if firebase-cli is standalone and configure correctly with task "
                )
                .append("setup", SB.Color.CYAN, True)
                .str()
            )
            process_killed = True
            self.__process.stop()
            self.__thread.join(2)
            self.__process.kill()
            self.__thread.join()

        output = self.__output
        if isinstance(output, BaseException):
            return Task.Result(args, error=output, success=self._skip)
        if process_killed:
            return Task.Result(
                args,
                error=ChildProcessError("Firebase-cli process was killed"),
                success=self._skip,
            )
        if output == False:
            return Task.Result(
                args,
                error=RuntimeError(
                    "Firebase-cli command return with code #"
                    + str(self.__process.exit_code)
                ),
                success=self._skip,
            )
        return Task.Result(args)

    def __run(self):
        self.__output = self.__process.try_run()
