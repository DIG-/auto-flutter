from typing import Optional

from .....core.config import Config
from .....core.string import SB
from .....core.utils.task.process.timeout import *
from ...identity import FirebaseTaskIdentity
from ...model._const import *


class FirebaseCheck(BaseProcessTimeoutTask):
    identity = FirebaseTaskIdentity("-firebase-check", "Checking firebase-cli", [], lambda: FirebaseCheck())

    def __init__(self, skip_on_failure: bool = False) -> None:
        super().__init__(ignore_failure=skip_on_failure, interval=5, timeout=30)

    def _create_process(self, args: Args) -> ProcessOrResult:
        return Process.create(
            Config.get_path(FIREBASE_CONFIG_KEY_PATH),
            arguments=[FIREBASE_DISABLE_INTERACTIVE_MODE.value, "--version"],
            environment=FIREBASE_ENV.value,
        )

    def _on_interval(self, process: Process, time: float, count: int) -> None:
        if count == 1:
            self._print("  Skill wating...")
        elif count == 3:
            self._print(SB().append("  It is taking some time...", SB.Color.YELLOW).str())
        return super()._on_interval(process, time, count)

    def _on_process_stop(self, process: Process, time: float, count: int) -> None:
        self._print(SB().append("  Stop process...", SB.Color.RED).str())
        return super()._on_process_stop(process, time, count)

    def _on_process_kill(self, process: Process, time: float, count: int) -> None:
        self._print(SB().append("  Kill process...", SB.Color.RED, True).str())
        return super()._on_process_kill(process, time, count)

    def _handle_process_exception(
        self,
        args: Args,
        process: Process,
        output: BaseException,
        message: Optional[str] = None,
    ) -> TaskResult:
        if isinstance(output, Process.ChildProcessStopped):
            builder = SB()
            if not message is None:
                builder.append(message, end="\n")
            builder.append("  Check if firebase-cli is standalone and configure correctly with task ")
            builder.append("setup", SB.Color.CYAN, True)
            message = builder.str()
        return super()._handle_process_exception(args, process, output, message)
