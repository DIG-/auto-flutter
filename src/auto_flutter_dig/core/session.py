from __future__ import annotations

from traceback import TracebackException

__all__ = ["Session"]


class __Session:
    def __init__(self, show_stacktrace: bool = False) -> None:
        self.show_stacktrace = show_stacktrace

    def format_exception(self, error: BaseException) -> str:
        if self.show_stacktrace:
            return "".join(TracebackException.from_exception(error).format())
        return str(error)


Session = __Session()
