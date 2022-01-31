from __future__ import annotations
from operator import itemgetter
from typing import Any, Dict, Optional, Tuple


class Arg(Tuple[str, Optional[str]]):
    def __new__(cls: type[Arg], argument: str, value: Optional[str]) -> Arg:
        argument = argument.strip()
        if not value is None:
            value = value.strip()
        return super().__new__(Arg, (argument, value))

    argument: str = property(itemgetter(0))
    value: Optional[str] = property(itemgetter(1))


class Args(Dict[str, Arg]):
    def add(self, arg: Arg):
        key = arg.argument.lstrip("-").lower()
        if not arg.argument.startswith("-"):
            key = "-#-" + key
        self[key] = arg

    def add(self, argument: str, value: Optional[str]):
        self.add(Arg(argument, value))


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
