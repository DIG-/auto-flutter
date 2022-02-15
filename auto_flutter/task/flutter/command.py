from typing import Optional

from ...core.config import Config
from ...core.utils import _If
from ...task.base.process import *
from ...task.flutter._const import (
    FLUTTER_CONFIG_KEY_PATH,
    FLUTTER_DISABLE_VERSION_CHECK,
)


class FlutterCommand(BaseProcessTask):
    def __init__(
        self,
        ignore_failure: bool = False,
        show_output_at_end: bool = False,
        command: Optional[List[str]] = None,
        show_output_running: bool = True,
        put_output_args: bool = False,
    ) -> None:
        super().__init__(ignore_failure, show_output_at_end)
        self._command: List[str] = _If.not_none(command, lambda x: x, lambda: [])
        self._show_output_running: bool = show_output_running
        self._put_output_args: bool = put_output_args

    def _create_process(self, args: Args) -> ProcessOrResult:
        if len(self._command) <= 0:
            return TaskResult(
                args,
                error=AssertionError("Flutter command require at least one command"),
            )
        flutter = Config.get_path(FLUTTER_CONFIG_KEY_PATH)
        self._command.append(FLUTTER_DISABLE_VERSION_CHECK)

        return Process.create(
            executable=flutter,
            arguments=self._command,
            writer=None if not self._show_output_running else self._print,
        )

    def _handle_process_finished(
        self, args: Args, process: Process, output: bool, message: Optional[str] = None
    ) -> TaskResult:
        if self._put_output_args:
            args.add_arg("output", process.output)
        return super()._handle_process_finished(args, process, output, message)
