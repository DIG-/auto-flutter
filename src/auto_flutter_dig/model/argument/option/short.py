from typing import Tuple

from ....core.utils import _Ensure
from .option import Option
from .valued import OptionWithValue

__all__ = ["ShortOption", "ShortOptionWithValue"]


class ShortOption(Option):
    def __init__(self, short: str, description: str) -> None:
        Option.__init__(self, description)
        self.short: str = _Ensure.instance(short, str, "short").lower().strip()
        if len(self.short) != 1:
            raise ValueError("Short option must have one character. Received: {}".format(short))

    def describe(self) -> Tuple[str, str]:
        return ("-" + self.short, self.description)


class ShortOptionWithValue(ShortOption, OptionWithValue):
    def __init__(self, short: str, description: str) -> None:
        ShortOption.__init__(self, short, "")
        OptionWithValue.__init__(self, description)
