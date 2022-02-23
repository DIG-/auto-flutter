from __future__ import annotations

from typing import Dict, Optional, Union

from .argument import Arg
from .option import LongOption, Option, PositionalOption, ShortOption

Value = Optional[str]
Argument = str
Group = str
Key = Union[Argument, Option]


class _Args:
    def __init__(
        self,
        initial: Dict[Group, Dict[Argument, Value]] = {},
        group: Optional[str] = None,
    ) -> None:
        self.__content: Dict[Group, Dict[Argument, Value]] = initial
        self.__selected_group: Optional[str] = group
        self.__selected_content: Dict[Argument, Value] = {}
        if not group is None:
            self.select_group(group)

    def __repr__(self) -> str:
        return self.__content.__repr__()

    def select_group(self, group: Group) -> _Args:
        self.__selected_group = group
        if group in self.__content:
            self.__selected_content = self.__content[group]
        else:
            self.__selected_content = {}
        return self

    def contains(self, key: Key) -> bool:
        key = self.__get_key(key)
        return key in self.__selected_content

    def get(self, key: Key) -> Value:
        key = self.__get_key(key)
        if key in self.__selected_content:
            return self.__selected_content[key]
        return None

    def add(self, key: Key, value: Value = None):
        key = self.__get_key(key)
        self.__selected_content[key] = value

    def remove(self, key: Key):
        key = self.__get_key(key)
        if key in self.__selected_content:
            self.__selected_content.pop(key)

    def group_contains(self, group: Group, key: Key) -> bool:
        if not group in self.__content:
            return False
        return self.__get_key(key) in self.__content[group]

    def group_get(self, group: Group, key: Key) -> Value:
        if not group in self.__content:
            return None
        key = self.__get_key(key)
        if key in self.__content[group]:
            return self.__content[group][key]
        return None

    def group_add(self, group: Group, key: Key, value: Value):
        key = self.__get_key(key)
        if not group in self.__content:
            self.__content[group] = {}
        self.__content[group][key] = value

    def group_remove(self, group: Group, key: Key):
        if not group in self.__content:
            return
        key = self.__get_key(key)
        if key in self.__content[group]:
            self.__content[group].pop(key)

    def __get_key(self, option: Key) -> Argument:
        key: Optional[Argument] = None
        if isinstance(option, Argument):
            key = option
        elif isinstance(option, Option):
            if isinstance(option, LongOption):
                key = option.long
            elif isinstance(option, ShortOption):
                key = option.short
            elif isinstance(option, PositionalOption):
                key = str(option.position)
            else:
                raise TypeError(
                    "Can not get correct type of Option: {}".format(
                        type(option).__name__
                    )
                )
        if key is None:
            raise KeyError("Can not extract key from `{}`".format(type(option)))
        return key.lower()


class Args(Dict[str, Arg]):
    def add(self, arg: Arg):
        key = arg.argument.lstrip("-").lower()
        if not arg.argument.startswith("-"):
            key = "-#-" + key
        self[key] = arg

    def add_arg(self, key: str, value: Optional[str] = None):
        self.add(Arg("--" + key, value))

    def contains(self, option: Union[str, Option]) -> bool:
        return Args.__get_key(option) in self

    def get_value(self, option: Union[str, Option]) -> Optional[str]:
        key = Args.__get_key(option)
        if not key in self:
            return None
        if key.startswith("-"):
            return self[key].argument
        return self[key].value

    @staticmethod
    def __get_key(option: Union[str, Option]) -> str:
        key: Optional[str] = None
        if isinstance(option, str):
            key = option
        elif isinstance(option, Option):
            if isinstance(option, LongOption):
                key = option.long
            elif isinstance(option, ShortOption):
                key = option.short
            elif isinstance(option, PositionalOption):
                key = "-" + str(option.position)
            else:
                raise TypeError(
                    "Can not get correct type of Option: {}".format(
                        type(option).__name__
                    )
                )
        if key is None:
            raise KeyError("Can not extract key from `{}`".format(type(option)))
        return key.lower()
