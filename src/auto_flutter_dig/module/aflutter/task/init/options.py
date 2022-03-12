from __future__ import annotations

from typing import Dict, Generic, Iterable, Optional, Type, TypeVar, Union

from .....core.config import Config
from .....model.argument.option import *
from .....model.argument.option.error import OptionInvalidFormat, OptionNotFound, OptionRequireValue
from .....model.task import *
from ...config.const import AFLUTTER_CONFIG_ENABLE_STACK_STRACE
from ..help import HelpTask

Argument = str
Group = str
GroupedOptions = Dict[Group, Option]
OptionsByArgument = Dict[Argument, GroupedOptions]

T = TypeVar("T", bound=Option)


class _Helper(Generic[T]):
    def __init__(self, option: T, group: Union[Group, TaskIdentity], cls: Type[T]) -> None:
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

    def into(self, target: Dict[Argument, Dict[Group, _Helper[T]]]):
        if not self.argument in target:
            target[self.argument] = {}
        target[self.argument][self.group] = self


class _ShortOptionMaybeWithValue(ShortOptionWithValue):
    ...


class _LongOptionMaybeWithValue(LongOptionWithValue):
    ...


class ParseOptionsTask(Task):
    __option_help = LongShortOption("h", "help", "Show help of task")
    __option_stack_trace = LongOption("stack-trace", "Enable stack trace of errors")

    def __init__(self, identity: TaskIdentity, arguments: List[str]) -> None:
        super().__init__()
        self._task_identity: TaskIdentity = identity
        self._input = arguments

    def describe(self, args: Args) -> str:
        return "Parsing arguments"

    def execute(self, args: Args) -> TaskResult:
        from .....core.task import TaskManager  # pylint: disable=import-outside-toplevel

        long_options: Dict[Argument, Dict[Group, _Helper[LongOption]]] = {}
        short_options: Dict[Argument, Dict[Group, _Helper[ShortOption]]] = {}
        positional_options: Dict[Argument, Dict[Group, _Helper[PositionalOption]]] = {}
        option_all: List[_Helper[OptionAll]] = []

        # Separate and identify options by type
        for identity in TaskManager._task_stack.copy():  # pylint: disable=protected-access
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

        _Helper(ParseOptionsTask.__option_help, "aflutter", ShortOption).into(short_options)
        _Helper(ParseOptionsTask.__option_help, "aflutter", LongOption).into(long_options)
        _Helper(ParseOptionsTask.__option_stack_trace, "aflutter", LongOption).into(long_options)

        has_param: List[_Helper] = []
        maybe_has_param: Optional[_Helper[Union[LongOption, ShortOption]]] = None
        position_count = 0
        has_option_all = len(option_all) > 0
        for argument in self._input:
            # Last iteration require param
            if len(has_param) > 0:
                self.__append_argument_all(args, option_all, argument)  # OptionAll
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
                    self.__append_argument_all(args, option_all, argument)  # OptionAll
                    self.__append_argument(args, maybe_has_param, argument)
                    maybe_has_param = None
                    continue

            # Handle short option argument
            if size == 2 and argument[0] == "-":
                self.__append_argument_all(args, option_all, argument)  # OptionAll
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
                    raise OptionNotFound("Unrecognized command line option {argument}")

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
                    self.__append_argument_all(args, option_all, argument)  # OptionAll
                    continue
                else:
                    raise OptionInvalidFormat("Invalid argument group structure for command line option {argument}")

                ###########
                # OptionAll
                if not group is None:
                    self.__append_argument_all(
                        args,
                        # pylint: disable=cell-var-from-loop
                        filter(lambda x: x.group == group, option_all),
                        "-" + sub if len(sub) == 1 else "--" + sub,
                    )
                else:
                    self.__append_argument_all(
                        args,
                        option_all,
                        "-" + sub if len(sub) == 1 else "--" + sub,
                    )
                # OptionAll
                ###########

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
                        maybe_has_param = _Helper(_ShortOptionMaybeWithValue(sub, ""), group, ShortOption)
                        continue
                    elif has_option_all:
                        continue
                    else:
                        raise OptionNotFound("Unrecognized command line option {argument}")

                # Long argument
                if sub in long_options:
                    if group is None:
                        for _, helper_long in long_options[sub].items():
                            if helper_long.has_value:
                                has_param.append(helper_long)
                            else:
                                self.__append_argument(args, helper_long, None)
                        continue
                    if group in long_options[sub]:
                        helper_long = long_options[sub][group]
                        if helper_long.has_value:
                            has_param.append(helper_long)
                        else:
                            self.__append_argument(args, helper_long, None)
                        continue
                    # unregistered group
                    maybe_has_param = _Helper(_LongOptionMaybeWithValue(sub, ""), group, LongOption)
                    continue
                elif not group is None:
                    # unregistered option with group
                    maybe_has_param = _Helper(_LongOptionMaybeWithValue(sub, ""), group, LongOption)
                    continue
                elif has_option_all:
                    continue
                else:
                    raise OptionNotFound("Unrecognized command line option {argument}")

            else:
                # Positional argument
                self.__append_argument_all(args, option_all, argument)  # OptionAll
                pos = str(position_count)
                position_count += 1
                if not pos in positional_options:
                    if has_option_all:
                        continue
                    else:
                        raise OptionNotFound('Unrecognized positional command line "{argument}"')
                for group, helper_positional in positional_options[pos].items():
                    self.__append_argument(args, helper_positional, argument)

        if args.group_contains("aflutter", ParseOptionsTask.__option_help):
            TaskManager._task_stack.clear()  # pylint: disable=protected-access
            self._append_task(HelpTask.Stub(self._task_identity))

        if args.group_contains("aflutter", ParseOptionsTask.__option_stack_trace):
            Config.put_bool(
                AFLUTTER_CONFIG_ENABLE_STACK_STRACE,
                True,
            )

        return TaskResult(args)

    def __append_argument(self, args: Args, helper: _Helper, value: Optional[str]):
        option: Option = helper.option
        group: Group = helper.group
        if helper.has_value and value is None:
            raise OptionRequireValue("Command line {} requires value, but nothing found")
        if isinstance(option, OptionAll):
            assert not value is None
            args.group_add_all(group, option, value)
            return
        args.group_add(group, option, value)

    def __append_argument_all(self, args: Args, helper: Iterable[_Helper], argument: Argument):
        for helper_all in helper:
            self.__append_argument(args, helper_all, argument)
