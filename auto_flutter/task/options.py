from getopt import GetoptError, gnu_getopt
from sys import argv as sys_argv
from typing import List, Optional

from ..core.session import Session
from ..core.utils import _Dict, _Iterable
from ..model.argument import Arg, OptionAll
from ..model.task import *
from .help_stub import HelpStub


class ParseOptions(Task):
    option_stack_trace = Option(
        None, "aflutter-stack-trace", "Show stacktrace of task output"
    )
    __options = {
        "stack-trace": Option(
            None,
            "aflutter-stack-trace",
            "Show stack trace of task output error",
            False,
            True,
        ),
        "help": Option("h", "help", "Show help of task", False, True),
    }

    identity = TaskIdentity(
        "-parse-options",
        "Parsing arguments",
        _Dict.flatten(__options),
        lambda: ParseOptions(),
    )

    def execute(self, args: Args) -> TaskResult:
        # Fill options list with current tasks
        from ..core.task.manager import TaskManager

        options: List[Option] = self.identity.options.copy()
        for task in TaskManager._task_stack:
            options.extend(task.options)
        skip = (
            not _Iterable.first_or_none(options, lambda x: isinstance(x, OptionAll))
            is None
        )

        if skip:
            encoder = OptionAll.ArgsEncode(args)
            for arg in sys_argv[2:]:
                if arg == "--aflutter-stack-trace":
                    Session.show_stacktrace = True
                    continue
                elif arg in ("-h", "--help"):
                    TaskManager._task_stack.clear()
                    TaskManager.add(HelpStub(sys_argv[1]))
                encoder.add(arg)
            return TaskResult(args)

        short = ""
        long: List[str] = []
        for option in options:
            short += option.short_formatted()
            long_fmt = option.long_formatted()
            if not long_fmt is None:
                long.append(long_fmt)
        try:
            opts, positional = gnu_getopt(sys_argv[2:], short, long)
        except GetoptError as error:
            return TaskResult(args, error, success=False)

        for opt, value in opts:
            opt_strip = opt.lstrip("-")
            found: Optional[Option] = None
            if len(opt_strip) <= 2:
                found = _Iterable.first_or_none(
                    options, lambda option: option.short == opt_strip
                )
            else:
                found = _Iterable.first_or_none(
                    options, lambda option: option.long == opt_strip
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
        if args.contains(self.__options["help"]):
            TaskManager._task_stack.clear()
            TaskManager.add(HelpStub(sys_argv[1]))

        return TaskResult(args)
