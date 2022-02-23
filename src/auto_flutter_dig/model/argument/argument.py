from __future__ import annotations

from typing import Optional

from ...core.utils import _Ensure


class Arg:
    def __init__(self, argument: str, value: Optional[str]) -> None:
        self.argument: str = _Ensure.instance(argument, str, "argument").strip()
        self.value: Optional[str] = _Ensure.type(value, str, "value")
        if not self.value is None:
            self.value = self.value.strip()

    def __repr__(self) -> str:
        return "{cls}(\nargument={argument}\nvalue={value}\n)".format(
            cls=type(self).__name__, argument=self.argument, value=self.value
        )
