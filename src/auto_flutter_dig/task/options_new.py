from pprint import pprint
from sys import argv as sys_argv
from typing import Dict, Optional

from ..model.argument.option_all import OptionAll
from ..model.task import *

Argument = str
Group = str
GroupedOptions = Dict[Group, Option]
OptionsByArgument = Dict[Argument, GroupedOptions]


class NewParseOptions(Task):
    def describe(self, args: Args) -> str:
        return "New Parsing arguments"

    def execute(self, args: Args) -> TaskResult:
        from ..core.task import TaskManager

        long_options: OptionsByArgument = {}
        short_options: OptionsByArgument = {}
        option_all: List[Group] = []

        for identity in TaskManager._task_stack.copy():
            for option in identity.options:
                if isinstance(option, OptionAll):
                    option_all.append(identity.group)
                    continue
                if not option.short is None and len(option.short) == 1:
                    self.__insert_option(
                        short_options, option.short, identity.group, option
                    )
                if not option.long is None and len(option.long) > 1:
                    self.__insert_option(
                        long_options, option.long, identity.group, option
                    )
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
                            self.__append_arg(args, sub, long_options[sub], None)
                            continue
                    else:
                        if group in long_options[sub]:
                            v_group: GroupedOptions = {group: long_options[sub][group]}
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
