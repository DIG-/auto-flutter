from __future__ import annotations
from ast import arguments, operator
from json import load
from operator import itemgetter
from re import S
from typing import Any, Dict, Optional, Tuple


class Args(Tuple[str, str, Optional[str]]):
    def __new__(cls: type[Args], argument: str, value: Optional[str]) -> Args:
        argument = argument.strip()
        key = argument.lstrip("-").lower()
        if not argument.startswith("-"):
            key = "-#-" + key
        return super().__new__(Args, (key, argument, value))

    key: str = property(itemgetter(0))
    argument: str = property(itemgetter(1))
    value: Optional[str] = property(itemgetter(2))


class Option(Tuple[Optional[str], Optional[str], str, bool]):
    def __new__(
        cls: type[Option],
        short: Optional[str],
        long: Optional[str],
        description: str,
        value: bool = False,
    ) -> Option:
        if (short is None or len(short) == 0) and (long is None or len(long) == 0):
            raise ValueError("Require at least short or long option")
        return super().__new__(Option, (short, long, description, value))

    short: Optional[str] = property(itemgetter(0))
    long: Optional[str] = property(itemgetter(1))
    description: str = property(itemgetter(2))
    has_value: bool = property(itemgetter(3))

    def short_formatted(self) -> str:
        if self.short is None:
            return ""
        if self.has_value:
            return self.short + ":"
        return self.short

    def long_formatted(self) -> Optional[str]:
        if self.long is None:
            return None
        if self.has_value:
            return self.long + "="
        return self.short
