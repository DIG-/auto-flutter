from typing import Tuple

from .long import LongOption, LongOptionWithValue
from .short import ShortOption, ShortOptionWithValue

__all__ = ["LongShortOption", "LongShortOptionWithValue"]


class LongShortOption(LongOption, ShortOption):
    def __init__(self, short: str, long: str, description: str) -> None:
        LongOption.__init__(self, long, "")
        ShortOption.__init__(self, short, description)

    def describe(self) -> Tuple[str, str]:
        return ("-{}, --{}".format(self.short, self.long), self.description)


class LongShortOptionWithValue(LongOptionWithValue, ShortOptionWithValue):
    def __init__(self, short: str, long: str, description: str) -> None:
        LongOptionWithValue.__init__(self, long, "")
        ShortOptionWithValue.__init__(self, short, description)
