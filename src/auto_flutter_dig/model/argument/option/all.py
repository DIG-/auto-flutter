from typing import Optional, Tuple

from ..arguments import Arg, Args
from .option import Option

__all__ = ["OptionAll"]


class OptionAll(Option):
    def __init__(self) -> None:
        super().__init__("")

    def describe(self) -> Tuple[str, str]:
        return ("", "Accept everything")

    ## Must be deprecated
    class ArgsEncode:
        def __init__(self, args: Args) -> None:
            self._args = args
            self._count = 0

        def add(self, argument: str):
            self._args["-{}-".format(self._count)] = Arg(argument, None)
            self._count += 1

    ## Must be deprecated
    class ArgsDecode:
        def __init__(self, args: Args) -> None:
            self._args = args

        def get(self, position: int) -> Optional[str]:
            index = "-{}-".format(position)
            if not index in self._args:
                return None
            return self._args[index].argument

        def all(self) -> map[str]:
            return map(lambda x: x[1].argument, self._args.items())
