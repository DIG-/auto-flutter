from typing import Iterable, Mapping, Optional

from ..arguments import Arg, Args


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

    def all(self) -> Iterable[str]:
        return map(lambda x: x[1].argument, self._args.items())
