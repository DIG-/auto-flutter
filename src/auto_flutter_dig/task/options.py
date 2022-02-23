from getopt import GetoptError, gnu_getopt
from sys import argv as sys_argv
from typing import List, Optional

from ..core.session import Session
from ..core.utils import _Dict, _Iterable
from ..model.argument import Arg
from ..model.argument.option import (
    LongOption,
    LongShortOptionWithValue,
    Option,
    OptionAll,
    OptionWithValue,
    ShortOption,
)
from ..model.task import *
from .help_stub import HelpStub


class ParseOptions(Task):
    option_stack_trace = LongOption(
        "aflutter-stack-trace", "Show stacktrace of task output"
    )
    __options = {
        "stack-trace": LongOption(
            "aflutter-stack-trace", "Show stack trace of task output error"
        ),
        "help": LongShortOptionWithValue("h", "help", "Show help of task"),
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
            if isinstance(option, LongOption):
                if isinstance(option, OptionWithValue):
                    long.append(option.long + "=")
                else:
                    long.append(option.long)
                pass
            if isinstance(option, ShortOption):
                short += option.short
                if isinstance(option, OptionWithValue):
                    short += ":"
                pass
        try:
            opts, positional = gnu_getopt(sys_argv[2:], short, long)
        except GetoptError as error:
            return TaskResult(args, error, success=False)

        for opt, value in opts:
            opt_strip = opt.lstrip("-")
            found: Optional[Option] = None
            if len(opt_strip) == 1:
                found = _Iterable.first_or_none(
                    options,
                    lambda option: isinstance(option, ShortOption)
                    and option.short == opt_strip,
                )
            else:
                found = _Iterable.first_or_none(
                    options,
                    lambda option: isinstance(option, LongOption)
                    and option.long == opt_strip,
                )

            if found is None:
                # Argument is not parameter
                args.add(Arg(opt, None))
            elif isinstance(found, ShortOption):
                # Using short argument
                args.add(
                    Arg(
                        opt,
                        value if isinstance(found, OptionWithValue) else None,
                    )
                )
            elif isinstance(found, LongOption):
                args.add(
                    Arg(
                        "--" + found.long,
                        value if isinstance(found, OptionWithValue) else None,
                    )
                )
            else:
                raise TypeError(
                    "Unexpected instance of Option: {}".format(type(found).__name__)
                )

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
