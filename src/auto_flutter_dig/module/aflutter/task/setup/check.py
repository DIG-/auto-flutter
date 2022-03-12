from .....core.utils import _Ensure, _Iterable
from .....model.argument.option import LongOption, LongShortOption, Option
from .....model.task import *
from .....module.aflutter.identity import AflutterTaskIdentity

__all__ = ["AflutterSetupCheckTask", "AflutterLaunchTaskOption"]


class AflutterLaunchTaskOption(LongOption):
    def __init__(self, long: str, identity: TaskIdentity) -> None:
        super().__init__(long, identity.name)
        self.identity = _Ensure.instance(identity, TaskIdentity, "identity")


class _SetupCheckTaskIdentity(AflutterTaskIdentity):
    def __init__(self, options: List[Option]) -> None:
        super().__init__(
            "check",
            "Check if environment is correctly configured",
            options,
            lambda: AflutterSetupCheckTask(),
        )

    def add(self, name: str, identity: TaskIdentity):
        self.options.append(AflutterLaunchTaskOption(name, identity))


class AflutterSetupCheckTask(Task):
    __opt_all = LongShortOption("a", "all", "Run all checks (default)")

    identity: _SetupCheckTaskIdentity = _SetupCheckTaskIdentity([__opt_all])

    def describe(self, args: Args) -> str:
        return ""

    def execute(self, args: Args) -> TaskResult:
        to_run: List[AflutterLaunchTaskOption] = []
        if args.contains(self.__opt_all):
            to_run = list(_Iterable.is_instance(self.identity.options, AflutterLaunchTaskOption))
        else:
            for option in self.identity.options:
                if option == self.__opt_all:
                    continue
                if args.contains(option) and isinstance(option, AflutterLaunchTaskOption):
                    to_run.append(option)

        if len(to_run) <= 0:
            self._uptade_description(self.identity.name)
            return TaskResult(args, error=LookupError("No environment check are available"))

        for opt in to_run:
            self._append_task(opt.identity)
        return TaskResult(args)
