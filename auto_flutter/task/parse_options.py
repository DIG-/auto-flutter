from getopt import GetoptError, gnu_getopt
from sys import argv as sys_argv
from typing import List, Optional

from ..core.session import Session
from ..core.utils import _Iterable
from ..model.argument import Arg, OptionAll
from ..model.task import Task


class ParseOptions(Task):
    identity = Task.Identity(
        "-parse-options",
        "Parsing arguments",
        [
            Task.Identity.Option(
                None, "aflutter-stack-trace", "Show stacktrace of task output"
            )
        ],
        lambda: ParseOptions(),
    )

    def __init__(self, tasks: List[Task]) -> None:
        super().__init__()
        self._options: List[Task.Identity.Option] = []
        for task in tasks:
            self._options.extend(task.identity.options)
        self._skip: bool = (
            not _Iterable.first_or_none(
                self._options, lambda x: isinstance(x, OptionAll)
            )
            is None
        )

    def execute(self, args: Task.Args) -> Task.Result:
        if self._skip:
            for arg in sys_argv[2:]:
                if arg == "--aflutter-stack-trace":
                    Session.show_stacktrace = True
                    continue
                args.add(Arg(arg, None))
            return Task.Result(args)

        short = ""
        long: List[str] = ["aflutter-stack-trace"]
        for option in self._options:
            short += option.short_formatted()
            long_fmt = option.long_formatted()
            if not long_fmt is None:
                long.append(long_fmt)
        try:
            opts, positional = gnu_getopt(sys_argv[2:], short, long)
        except GetoptError as error:
            return Task.Result(args, error, success=False)

        for opt, value in opts:
            opt_strip = opt.lstrip("-")
            found: Optional[Task.Identity.Option] = None
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

        if "aflutter-stack-trace" in args:
            Session.show_stacktrace = True
            args.pop("aflutter-stack-trace")

        return Task.Result(args)
