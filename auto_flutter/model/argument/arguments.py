from itertools import chain
from typing import Dict, List

from .argument import Arg


class Args(Dict[str, Arg]):
    def add(self, arg: Arg):
        key = arg.argument.lstrip("-").lower()
        if not arg.argument.startswith("-"):
            key = "-#-" + key
        self[key] = arg

    def to_command_arg(self) -> List[str]:
        mapped = map(lambda x: x[1], self.items())
        return list(filter(None.__ne__, chain(*mapped)))
