from __future__ import annotations

from typing import Optional

from ...core.utils import _Ensure, _If


class Option:
    def __init__(
        self,
        short: Optional[str],
        long: Optional[str],
        description: str,
        value: bool = False,
        hidden: bool = False,
    ) -> None:
        self.short: Optional[str] = _If.not_none(
            _Ensure.type(short, str, "short"), lambda x: x.strip(), lambda: None
        )
        self.long: Optional[str] = _If.not_none(
            _Ensure.type(long, str, "long"), lambda x: x.strip(), lambda: None
        )
        self.description: str = _Ensure.instance(description, str, "description")
        self.has_value: bool = _Ensure.instance(value, bool, "value")
        self.hidden: bool = _Ensure.instance(hidden, bool, "hidden")

        if not self.short is None and len(self.short) != 1:
            raise ValueError("Short option must have only one character")
        if not self.long is None and len(self.long) <= 1:
            raise ValueError("Long option must have more than one character")
        if self.short is None and self.long is None:
            raise ValueError("Require at least short or long option")
        pass

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
        return self.long
