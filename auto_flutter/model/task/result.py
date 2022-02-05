from __future__ import annotations

from operator import itemgetter
from typing import Optional, Tuple

from ...core.utils import _Ensure
from ..argument import Args


class TaskResult(Tuple[Args, Optional[BaseException], Optional[str], bool]):
    def __new__(
        cls: type[TaskResult],
        args: Args,
        error: Optional[BaseException] = None,
        message: Optional[str] = None,
        success: Optional[bool] = None,
    ) -> TaskResult:
        _Ensure.type(args, Args, "args")
        _Ensure.type(error, BaseException, "error")
        _Ensure.type(message, str, "message")
        _Ensure.type(success, bool, "success")

        if success is None:
            if error is None:
                success = True
            else:
                success = False

        return super().__new__(
            TaskResult, (_Ensure.not_none(args), error, message, success)
        )

    args: Args = property(itemgetter(0))
    error: Optional[BaseException] = property(itemgetter(1))
    message: Optional[str] = property(itemgetter(2))
    success: bool = property(itemgetter(3))
