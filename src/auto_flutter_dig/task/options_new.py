from __future__ import annotations

from sys import argv as sys_argv
from typing import Dict, Generic, Optional, Type, TypeVar

from ..model.argument.option import *
from ..model.task import *

Argument = str
Group = str
GroupedOptions = Dict[Group, Option]
OptionsByArgument = Dict[Argument, GroupedOptions]

T = TypeVar("T", bound=Option)


class _Helper(Generic[T]):
    def __init__(self, option: T, identity: TaskIdentity, cls: Type[T]) -> None:
        self.option: T = option
        self.identity: TaskIdentity = identity
        self.group = identity.group
        self.has_value: bool = isinstance(option, OptionWithValue)
        self.argument: str = ""
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

    def into(self, target: Dict[str, T]):
        target[self.argument] = self


class NewParseOptions(Task):
    def describe(self, args: Args) -> str:
        return "New Parsing arguments"

    def execute(self, args: Args) -> TaskResult:
        from ..core.task import TaskManager

        long_options: Dict[str, _Helper[LongOption]] = {}
        short_options: Dict[str, _Helper[ShortOption]] = {}
        positional_options: Dict[str, _Helper[PositionalOption]] = {}
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
                    _Helper(option, identity, PositionalOption).into(
                        positional_options)
            pass

        positional: List[str] = []
        input = sys_argv[2:]
        param_next = False
        param_option: Optional[Argument] = None
        param_groups: Optional[GroupedOptions] = None
        maybe_has_param = False
        maybe_has_param_option: Optional[Argument] = None
        maybe_has_param_group: Optional[Group] = None
        for argument in input:
            if param_next:
                param_next = False
                assert not param_option is None
                assert not param_groups is None
                self.__append_arg(args, param_option, param_groups, argument)
                param_groups = None
                continue

            size = len(argument)
            if maybe_has_param:
                maybe_has_param = False
                assert not maybe_has_param_option is None
                if size > 1 and argument[0] == "-":
                    self.__appeng_arg_directly(
                        args, maybe_has_param_option, maybe_has_param_group, None
                    )
                    maybe_has_param_option = None
                    maybe_has_param_group = None
                else:
                    self.__appeng_arg_directly(
                        args, maybe_has_param_option, maybe_has_param_group, argument
                    )
                    maybe_has_param_option = None
                    maybe_has_param_group = None
                    continue

            if size == 2 and argument[0] == "-":
                sub = argument[1:].lower()
                if sub in short_options:
                    if any(
                        option.has_value for grp, option in short_options[sub].items()
                    ):
                        param_next = True
                        param_option = sub
                        param_groups = short_options[sub]
                        continue
                    else:
                        self.__append_arg(args, sub, short_options[sub], None)
                        continue
                else:
                    # Unregistered option
                    maybe_has_param = True
                    maybe_has_param_group = None
                    maybe_has_param_option = sub
                    continue
            elif size >= 4 and argument[0] == "-" and argument[1] == "-":
                split = argument[2:].lower().split(":")
                split_len = len(split)
                if split_len == 1:
                    sub = split[0]
                    group = None
                elif split_len == 2:
                    sub = split[1]
                    group = split[0]
                else:
                    raise AssertionError(
                        "Invalid argument group type: {}".format(split)
                    )
                if sub in long_options:
                    if group is None:
                        if any(
                            option.has_value
                            for grp, option in long_options[sub].items()
                        ):
                            param_next = True
                            param_option = sub
                            param_groups = long_options[sub]
                            continue
                        else:
                            self.__append_arg(
                                args, sub, long_options[sub], None)
                            continue
                    else:
                        if group in long_options[sub]:
                            v_group: GroupedOptions = {
                                group: long_options[sub][group]}
                            if long_options[sub][group].has_value:
                                param_next = True
                                param_option = sub
                                param_groups = v_group
                                continue
                            else:
                                self.__append_arg(args, sub, v_group, None)
                                continue
                        else:
                            # unregistered group
                            maybe_has_param = True
                            maybe_has_param_option = sub
                            maybe_has_param_group = group
                            continue
                else:  # unregistered option
                    maybe_has_param = True
                    maybe_has_param_option = sub
                    maybe_has_param_group = group
                    continue

            else:
                positional.append(argument)
            pass

        self._print("Positional: {}".format(str(positional)))

        return TaskResult(args)

    def __insert_option(
        self,
        options: OptionsByArgument,
        argument: Argument,
        group: Group,
        option: Option,
    ):
        if not argument in options:
            options[argument] = {}
        options[argument][group] = option

    def __append_arg(
        self,
        args: Args,
        argument: Argument,
        grouped: GroupedOptions,
        value: Optional[str],
    ):
        for group, option in grouped.items():
            self.__appeng_arg_directly(args, argument, group, value)
        pass

    def __appeng_arg_directly(
        self,
        arg: Args,
        argument: Argument,
        group: Optional[Group],
        value: Optional[str],
    ):
        self._print(
            "--{argument}:{group} {value}".format(
                argument=argument, group=group, value=value
            )
        )
        pass
