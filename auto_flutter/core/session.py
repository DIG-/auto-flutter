from __future__ import annotations
from typing import Optional


class _Session:
    __instance: Optional[_Session] = None

    def instance() -> _Session:
        if _Session.__instance is None:
            _Session.__instance = _Session()
        return _Session.__instance

    def __init__(self, show_stacktrace: bool = False) -> None:
        self.show_stacktrace = show_stacktrace


Session = _Session.instance()
