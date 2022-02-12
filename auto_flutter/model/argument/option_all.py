from __future__ import annotations

from .option import Option


class OptionAll(Option):
    def __init__(self, task: bool = True) -> None:
        super().__init__(
            None,
            "#-#-#-#-#",
            "This task does not parse options, it bypass directly to command"
            if task
            else "This action does not parse options, it bypass directly to command",
            False,
        )
