import re
from itertools import chain
from typing import Dict, Final, List, Optional, Union

from .argument import Arg
from .option import Option


class Args(Dict[str, Arg]):
    def add(self, arg: Arg):
        key = arg.argument.lstrip("-").lower()
        if not arg.argument.startswith("-"):
            key = "-#-" + key
        self[key] = arg

    def add_arg(self, key: str, value: Optional[str] = None):
        self.add(Arg("--" + key, value))

    def to_command_arg(self) -> List[str]:
        mapped = map(lambda x: x[1], self.items())
        return list(filter(None.__ne__, chain(*mapped)))

    def contains(self, option: Union[str, Option]) -> bool:
        return Args.__get_key(option) in self

    def get_value(self, option: Union[str, Option]) -> Optional[str]:
        key = Args.__get_key(option)
        if not key in self:
            return None
        if key.startswith("-"):
            return self[key].argument
        return self[key].value

    def __get_key(option: Union[str, Option]) -> str:
        key: str = None
        if isinstance(option, str):
            key = option
        elif isinstance(option, Option):
            if option.long is None:
                key = option.short
            else:
                key = option.long
        if key is None:
            raise KeyError("Can not extract key from `{}`".format(type(option)))
        return key.lower()
