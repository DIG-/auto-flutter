from __future__ import annotations

from typing import Optional

from .option import Option


class OptionAll(Option):
    def __new__(cls: type[OptionAll], description: Optional[str] = None) -> OptionAll:
        return super().__new__(
            OptionAll,
            None,
            None,
            "This task does not parse options, it bypass directly to command"
            if description is None
            else description,
            False,
        )
