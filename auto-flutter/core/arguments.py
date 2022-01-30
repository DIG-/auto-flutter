from __future__ import annotations
from ast import arguments, operator
from operator import itemgetter
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
