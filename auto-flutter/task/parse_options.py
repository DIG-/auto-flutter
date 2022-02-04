from getopt import GetoptError, getopt
from typing import List, Optional
from sys import argv as sys_argv
from ..core.task import Task, TaskIdentity, TaskResult
from ..core.arguments import Arg, Args, Option, OptionAll
from ..core.utils import _Iterable


class ParseOptions(Task):
    identity = TaskIdentity(
        "-parse-options", "Parsing arguments", [], lambda: ParseOptions()
    )

    def __init__(self, tasks: List[Task]) -> None:
        super().__init__()
        self._options: List[Option] = []
        for task in tasks:
            self._options.extend(task.identity.options)
        self._skip: bool = (
            not _Iterable.first_or_none(
                self._options, lambda x: isinstance(x, OptionAll)
            )
            is None
        )

    def execute(self, args: Args) -> TaskResult:
        if self._skip:
            for arg in sys_argv[2:]:
                args.add(Arg(arg, None))
            return Task.Result(args)

        short = ""
        long: List[str] = []
        for option in self._options:
            short += option.short_formatted()
            long_fmt = option.long_formatted()
            if not long_fmt is None:
                long.append(long_fmt)
        try:
            opts, positional = getopt(sys_argv[2:], short, long)
        except GetoptError as error:
            return TaskResult(args, error, success=False)

        for opt, value in opts:
            opt_strip = opt.lstrip("-")
            found: Optional[Option] = None
            if len(opt_strip) <= 2:
                found = _Iterable.first_or_none(
                    self._options, lambda option: option.short == opt_strip
                )
            else:
                found = _Iterable.first_or_none(
                    self._options, lambda option: option.long == opt_strip
                )

            if found is None:
                # Argument is not parameter
                args.add(Arg(opt, None))
            elif found.long is None:
                # Using short argument
                args.add(Arg(opt, value if found.has_value else None))
            else:
                args.add(Arg("--" + found.long, value if found.has_value else None))

        i = 0
        for value in positional:
            args["-" + str(i)] = Arg(value, None)
            i += 1

        return TaskResult(args)

    def _bypass_parse(self, args: Args) -> TaskResult:
        pass
