from __future__ import annotations

from operator import itemgetter
from typing import Optional, Tuple

from ...core.utils import _Ensure


class Arg(Tuple[str, Optional[str]]):
    def __new__(cls: type[Arg], argument: str, value: Optional[str]) -> Arg:
        _Ensure.type(argument, str, "argument")
        _Ensure.type(value, str, "value")
        argument = argument.strip()
        if not value is None:
            value = value.strip()
        return super().__new__(Arg, (argument, value))

    argument: str = property(itemgetter(0))
    value: Optional[str] = property(itemgetter(1))
