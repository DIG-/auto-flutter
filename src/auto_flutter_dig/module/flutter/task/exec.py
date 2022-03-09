from ....model.argument.option import OptionAll
from ....task.base.process import *
from ..identity import FlutterTaskIdentity
from .command import FlutterCommandTask


class FlutterExecTask(FlutterCommandTask):
    __opt_all = OptionAll()
    identity = FlutterTaskIdentity(
        "exec",
        "Execute flutter command",
        [__opt_all],
        lambda: FlutterExecTask(),  # pylint: disable=unnecessary-lambda
        allow_more=True,
    )

    def __init__(self) -> None:
        super().__init__(describe="Executing flutter command", require_project=False)
        self._can_print_content = True  # Always print flutter exec

    def _create_process(self, args: Args) -> ProcessOrResult:
        self._command = list(args.get_all(self.__opt_all))
        return super()._create_process(args)
