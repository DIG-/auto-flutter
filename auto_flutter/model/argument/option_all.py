from __future__ import annotations

from typing import Optional

from .arguments import Arg, Args
from .option import Option


class OptionAll(Option):
    def __init__(self, task: bool = True) -> None:
        super().__init__(
            None,
            "#-#-#-#-#",
            "This task does not parse options, it bypass directly to command"
            if task
            else "This action does not parse options, it bypass directly to command",
            False,
        )

    class ArgsEncode:
        def __init__(self, args: Args) -> None:
            self._args = args
            self._count = 0

        def add(self, argument: str):
            self._args["-{}-".format(self._count)] = Arg(argument, None)
            self._count += 1

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
