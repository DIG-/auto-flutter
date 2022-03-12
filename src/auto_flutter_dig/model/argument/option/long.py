from typing import Tuple

from ....core.utils import _Ensure
from .option import Option
from .valued import OptionWithValue

__all__ = ["LongOption", "LongOptionWithValue"]


class LongOption(Option):
    def __init__(self, long: str, description: str) -> None:
        Option.__init__(self, description)
        self.long: str = _Ensure.instance(long, str, "long").lower().strip()
        if len(self.long) <= 1:
            raise ValueError("Long option must have more than one character. Received: {}".format(long))

    def describe(self) -> Tuple[str, str]:
        return ("--" + self.long, self.description)


class LongOptionWithValue(LongOption, OptionWithValue):
    def __init__(self, long: str, description: str) -> None:
        LongOption.__init__(self, long, "")
        OptionWithValue.__init__(self, description)
