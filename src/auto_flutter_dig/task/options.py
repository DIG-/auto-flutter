from __future__ import annotations

from sys import argv as sys_argv
from typing import Dict, Generic, Optional, Type, TypeVar, Union

from ..core.session import Session
from ..model.argument.option import *
from ..model.argument.option.error import (
    OptionInvalidFormat,
    OptionNotFound,
    OptionRequireValue,
)
from ..model.task import *
from ..task.help import Help

Argument = str
Group = str
GroupedOptions = Dict[Group, Option]
OptionsByArgument = Dict[Argument, GroupedOptions]

T = TypeVar("T", bound=Option)


class _Helper(Generic[T]):
    def __init__(
        self, option: T, group: Union[Group, TaskIdentity], cls: Type[T]
    ) -> None:
        self.option: T = option
        self.group: Group = ""
        if isinstance(group, Group):
            self.group = group
        elif isinstance(group, TaskIdentity):
            self.group = group.group

        self.has_value: bool = isinstance(option, OptionWithValue)
        self.argument: Argument = ""
        if cls is LongOption:
            assert isinstance(option, LongOption)
            self.argument = option.long
        elif cls is ShortOption:
            assert isinstance(option, ShortOption)
            self.argument = option.short
        elif cls is PositionalOption:
            assert isinstance(option, PositionalOption)
            self.argument = str(option.position)
        pass

    def into(self, target: Dict[Argument, Dict[Group, _Helper[T]]]):
        if not self.argument in target:
            target[self.argument] = {}
        target[self.argument][self.group] = self


class _ShortOptionMaybeWithValue(ShortOptionWithValue):
    ...


class _LongOptionMaybeWithValue(LongOptionWithValue):
    ...


class ParseOptions(Task):
    __option_help = LongShortOption("h", "help", "Show help of task")
    __option_stack_trace = LongOption("stack-trace", "Enable stack trace of errors")

    def describe(self, args: Args) -> str:
        return "Parsing arguments"

    def execute(self, args: Args) -> TaskResult:
        from ..core.task import TaskManager

        long_options: Dict[Argument, Dict[Group, _Helper[LongOption]]] = {}
        short_options: Dict[Argument, Dict[Group, _Helper[ShortOption]]] = {}
        positional_options: Dict[Argument, Dict[Group, _Helper[PositionalOption]]] = {}
        option_all: List[_Helper[OptionAll]] = []

        # Separate and identify options by type
        for identity in TaskManager._task_stack.copy():
            for option in identity.options:
                if isinstance(option, OptionAll):
                    option_all.append(_Helper(option, identity, OptionAll))
                    continue
                if isinstance(option, LongOption):
                    _Helper(option, identity, LongOption).into(long_options)
                if isinstance(option, ShortOption):
                    _Helper(option, identity, ShortOption).into(short_options)
                if isinstance(option, PositionalOption):
                    _Helper(option, identity, PositionalOption).into(positional_options)
            pass
        _Helper(ParseOptions.__option_help, "aflutter", ShortOption).into(short_options)
        _Helper(ParseOptions.__option_help, "aflutter", LongOption).into(long_options)
        _Helper(ParseOptions.__option_stack_trace, "aflutter", LongOption).into(
            long_options
        )

        input = sys_argv[2:]
        has_param: List[_Helper] = []
        maybe_has_param: Optional[_Helper[Union[LongOption, ShortOption]]] = None
        position_count = 0
        has_option_all = len(option_all) > 0
        for argument in input:
            for helper_all in option_all:
                self.__append_argument(args, helper_all, argument)

            # Last iteration require param
            if len(has_param) > 0:
                for helper_has_param in has_param:
                    self.__append_argument(args, helper_has_param, argument)
                has_param = []
                continue

            size = len(argument)
            # Last iteration maybe require param
            if not maybe_has_param is None:
                if size > 1 and argument[0] == "-":
                    if isinstance(maybe_has_param.option, ShortOption):
                        self.__append_argument(
                            args,
                            _Helper(
                                ShortOption(maybe_has_param.option.short, ""),
                                maybe_has_param.group,
                                ShortOption,
                            ),
                            None,
                        )
                    elif isinstance(maybe_has_param.option, LongOption):
                        self.__append_argument(
                            args,
                            _Helper(
                                LongOption(maybe_has_param.option.long, ""),
                                maybe_has_param.group,
                                LongOption,
                            ),
                            None,
                        )
                    maybe_has_param = None
                else:
                    self.__append_argument(args, maybe_has_param, argument)
                    maybe_has_param = None
                    continue

            # Handle short option argument
            if size == 2 and argument[0] == "-":
                sub = argument[1:].lower()
                if sub in short_options:
                    for group, helper_short in short_options[sub].items():
                        if helper_short.has_value:
                            has_param.append(helper_short)
                        else:
                            self.__append_argument(args, helper_short, None)
                    continue
                elif has_option_all:
                    continue
                else:
                    raise OptionNotFound(
                        "Unrecognized command line option {}".format(argument)
                    )

            elif size >= 4 and argument[0] == "-" and argument[1] == "-":

                split = argument[2:].lower().split(":")
                split_len = len(split)
                if split_len == 1:
                    sub = split[0]
                    group = None
                elif split_len == 2:
                    sub = split[1]
                    group = split[0]
                elif has_option_all:
                    continue
                else:
                    raise OptionInvalidFormat(
                        "Invalid argument group structure for command line option {}".format(
                            argument
                        )
                    )
                # Short argument with group
                if len(sub) == 1:
                    if sub in short_options:
                        for group, helper_short in short_options[sub].items():
                            if helper_short.has_value:
                                has_param.append(helper_short)
                            else:
                                self.__append_argument(args, helper_short, None)
                        continue
                    elif not group is None:
                        maybe_has_param = _Helper(
                            _ShortOptionMaybeWithValue(sub, ""), group, ShortOption
                        )
                        continue
                    elif has_option_all:
                        continue
                    else:
                        raise OptionNotFound(
                            "Unrecognized command line option {}".format(argument)
                        )

                # Long argument
                if sub in long_options:
                    if group is None:
                        for grp, helper_long in long_options[sub].items():
                            if helper_long.has_value:
                                has_param.append(helper_long)
                            else:
                                self.__append_argument(args, helper_long, None)
                        continue
                    else:
                        if group in long_options[sub]:
                            helper_long = long_options[sub][group]
                            if helper_long.has_value:
                                has_param.append(helper_long)
                            else:
                                self.__append_argument(args, helper_long, None)
                            continue
                        else:
                            # unregistered group
                            maybe_has_param = _Helper(
                                _LongOptionMaybeWithValue(sub, ""), group, LongOption
                            )
                            continue
                elif not group is None:
                    # unregistered option with group
                    maybe_has_param = _Helper(
                        _LongOptionMaybeWithValue(sub, ""), group, LongOption
                    )
                    continue
                elif has_option_all:
                    continue
                else:
                    raise OptionNotFound(
                        "Unrecognized command line option {}".format(argument)
                    )

            else:
                # Positional argument
                pos = str(position_count)
                position_count += 1
                if not pos in positional_options:
                    if has_option_all:
                        continue
                    else:
                        raise OptionNotFound(
                            'Unrecognized positional command line "{}"'.format(argument)
                        )
                for group, helper_positional in positional_options[pos].items():
                    self.__append_argument(args, helper_positional, argument)
            pass

        if args.group_contains("aflutter", ParseOptions.__option_help):
            TaskManager._task_stack.clear()
            self._append_task(Help.Stub(sys_argv[1]))

        Session.show_stacktrace = args.group_contains(
            "aflutter", ParseOptions.__option_stack_trace
        )

        return TaskResult(args)

    def __append_argument(self, args: Args, helper: _Helper, value: Optional[str]):
        option: Option = helper.option
        group: Group = helper.group
        if helper.has_value and value is None:
            raise OptionRequireValue(
                "Command line {} requires value, but nothing found"
            )
        if isinstance(option, OptionAll):
            assert not value is None
            args.group_add_all(group, option, value)
            return
        args.group_add(group, option, value)
